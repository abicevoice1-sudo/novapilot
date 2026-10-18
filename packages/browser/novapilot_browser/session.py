"""Playwright browser session: scoped navigation, actions, screenshots.

Safety model:
- Navigation is scoped to allowed_domains (empty = unrestricted, local dev).
- Only http(s) URLs; no file://, no custom schemes.
- Every action is audit-logged by the caller (the agent tool layer emits receipts).
- Approval gating lives in the tool layer: every browser tool requires approval.
"""

from __future__ import annotations

import logging
from pathlib import Path
from urllib.parse import urlparse

log = logging.getLogger("novapilot.browser")

_SNAPSHOT_JS = """
() => {
  const els = document.querySelectorAll(
    'a, button, input, select, textarea, [role="button"], [role="link"]'
  );
  const out = [];
  const seen = new Set();
  function selector(el) {
    if (el.id) return '#' + el.id;
    const parts = [];
    let node = el;
    for (let d = 0; d < 3 && node && node !== document.body; d++) {
      let part = node.tagName.toLowerCase();
      if (node.id) { parts.unshift('#' + node.id); break; }
      const cls = (node.className && typeof node.className === 'string'
        ? node.className.trim().split(/\\s+/)[0] : '');
      if (cls) part += '.' + cls;
      const sibs = node.parentElement
        ? [...node.parentElement.children].filter(c => c.tagName === node.tagName) : [];
      if (sibs.length > 1) part += `:nth-of-type(${sibs.indexOf(node) + 1})`;
      parts.unshift(part);
      node = node.parentElement;
    }
    return parts.join(' > ');
  }
  for (const el of els) {
    const r = el.getBoundingClientRect();
    if (r.width === 0 && r.height === 0) continue;
    const sel = selector(el);
    if (seen.has(sel)) continue;
    seen.add(sel);
    const name = (el.innerText || el.getAttribute('aria-label') || el.getAttribute('name')
      || el.getAttribute('placeholder') || el.value || '').trim().replace(/\\s+/g, ' ').slice(0, 80);
    out.push({role: el.tagName.toLowerCase(), type: el.type || '', name, selector: sel});
    if (out.length >= 60) break;
  }
  return out;
}
"""


class BrowserError(Exception):
    """Navigation outside scope, missing browser, action failure."""


class BrowserSession:
    def __init__(
        self,
        shots_dir: str | Path = "./browser-shots",
        allowed_domains: list[str] | None = None,
        headless: bool = True,
    ) -> None:
        self.shots_dir = Path(shots_dir)
        self.allowed_domains = [d.lower() for d in (allowed_domains or [])]
        self.headless = headless
        self._pw = None
        self._browser = None
        self._page = None
        self._shot_count = 0

    async def start(self) -> None:
        from playwright.async_api import async_playwright

        if self._browser is not None:
            return
        self.shots_dir.mkdir(parents=True, exist_ok=True)
        try:
            self._pw = await async_playwright().start()
            self._browser = await self._pw.chromium.launch(headless=self.headless)
            self._page = await self._browser.new_page(viewport={"width": 1280, "height": 800})
        except Exception as e:
            raise BrowserError(
                "Chromium could not start. Run: pip install playwright && playwright install chromium"
            ) from e
        log.info("browser session started (headless=%s)", self.headless)

    async def close(self) -> None:
        if self._browser is not None:
            await self._browser.close()
            self._browser = None
        if self._pw is not None:
            await self._pw.stop()
            self._pw = None

    def _require_page(self):
        if self._page is None:
            raise BrowserError("browser not started")
        return self._page

    def _check_scope(self, url: str) -> None:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            raise BrowserError(f"only http(s) URLs allowed: {url}")
        if not self.allowed_domains:
            return
        host = (parsed.hostname or "").lower()
        if not any(host == d or host.endswith("." + d) for d in self.allowed_domains):
            raise BrowserError(f"navigation outside scope ({', '.join(self.allowed_domains)}): {host}")

    async def open(self, url: str) -> dict:
        self._check_scope(url)
        page = self._require_page()
        try:
            resp = await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        except Exception as e:
            raise BrowserError(f"navigation failed: {e}") from e
        return {
            "url": page.url,
            "title": await page.title(),
            "status": resp.status if resp else None,
        }

    async def screenshot(self, label: str = "") -> str:
        """Take a screenshot; returns the file name (served via /api/shots)."""
        page = self._require_page()
        self._shot_count += 1
        name = f"shot-{self._shot_count:04d}.png"
        await page.screenshot(path=str(self.shots_dir / name))
        log.info("screenshot %s%s", name, f" ({label})" if label else "")
        return name

    async def read(self, max_chars: int = 8000) -> dict:
        page = self._require_page()
        text = await page.evaluate("() => document.body ? document.body.innerText : ''")
        text = " ".join(text.split())
        return {"url": page.url, "title": await page.title(), "text": text[:max_chars]}

    async def snapshot(self) -> list[dict]:
        page = self._require_page()
        return await page.evaluate(_SNAPSHOT_JS)

    async def _act(self, action: str, selector: str, **kwargs) -> dict:
        page = self._require_page()
        try:
            loc = page.locator(selector).first
            await loc.wait_for(state="visible", timeout=10000)
            if action == "click":
                await loc.click(timeout=10000)
            elif action == "fill":
                await loc.fill(kwargs["text"], timeout=10000)
            elif action == "select":
                await loc.select_option(kwargs["value"], timeout=10000)
            elif action == "press":
                await loc.press(kwargs["key"], timeout=10000)
        except Exception as e:
            raise BrowserError(f"{action} failed on {selector!r}: {e}") from e
        shot = await self.screenshot(label=f"{action} {selector}")
        return {"url": page.url, "shot": shot}

    async def click(self, selector: str) -> dict:
        return await self._act("click", selector)

    async def fill(self, selector: str, text: str) -> dict:
        return await self._act("fill", selector, text=text)

    async def select(self, selector: str, value: str) -> dict:
        return await self._act("select", selector, value=value)

    async def press(self, selector: str, key: str) -> dict:
        return await self._act("press", selector, key=key)

    async def back(self) -> dict:
        page = self._require_page()
        await page.go_back(wait_until="domcontentloaded", timeout=15000)
        shot = await self.screenshot(label="back")
        return {"url": page.url, "shot": shot}

    async def scroll(self, selector: str = "", direction: str = "down", pixels: int = 600) -> dict:
        """Scroll the page or an element. direction: up/down."""
        page = self._require_page()
        delta = pixels if direction == "down" else -pixels
        try:
            if selector:
                loc = page.locator(selector).first
                await loc.evaluate(f"(el) => el.scrollBy(0, {delta})")
            else:
                await page.evaluate(f"window.scrollBy(0, {delta})")
        except Exception as e:
            raise BrowserError(f"scroll failed: {e}") from e
        shot = await self.screenshot(label=f"scroll {direction}")
        return {"url": page.url, "shot": shot}

    async def hover(self, selector: str) -> dict:
        page = self._require_page()
        try:
            loc = page.locator(selector).first
            await loc.wait_for(state="visible", timeout=10000)
            await loc.hover(timeout=10000)
        except Exception as e:
            raise BrowserError(f"hover failed on {selector!r}: {e}") from e
        shot = await self.screenshot(label=f"hover {selector}")
        return {"url": page.url, "shot": shot}

    async def wait_for(
        self, selector: str = "", text: str = "", timeout_sec: int = 15
    ) -> dict:
        """Wait for an element (visible) or text to appear. At least one required."""
        page = self._require_page()
        if not selector and not text:
            raise BrowserError("wait_for needs a selector or text")
        try:
            if selector:
                await page.locator(selector).first.wait_for(
                    state="visible", timeout=timeout_sec * 1000
                )
            else:
                await page.get_by_text(text).first.wait_for(
                    state="visible", timeout=timeout_sec * 1000
                )
        except Exception as e:
            raise BrowserError(f"wait_for timed out after {timeout_sec}s: {e}") from e
        return {"url": page.url, "found": True}

    @property
    def current_url(self) -> str:
        return self._page.url if self._page else ""
