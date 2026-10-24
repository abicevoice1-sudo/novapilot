"""Browser session tests: scoped navigation, actions, screenshots. Fake session, no Chromium."""

import pytest
from actlet_agent.tools import ToolRegistry

from actlet_browser.session import BrowserError, BrowserSession
from actlet_browser.tools import register_browser_tools


class FakeSession:
    def __init__(self):
        self.opened = []
        self.shots = 0

    async def open(self, url):
        self.opened.append(url)
        return {"url": url, "title": "Fake", "status": 200}

    async def screenshot(self, label=""):
        self.shots += 1
        return f"shot-{self.shots:04d}.png"

    async def read(self, max_chars=8000):
        return {"url": "http://x/", "title": "Fake", "text": "hello world"}

    async def snapshot(self):
        return [{"role": "button", "type": "", "name": "Search", "selector": "#search"}]

    async def click(self, selector):
        return {"url": "http://x/", "shot": await self.screenshot()}

    async def fill(self, selector, text):
        return {"url": "http://x/", "shot": await self.screenshot()}

    async def select(self, selector, value):
        return {"url": "http://x/", "shot": await self.screenshot()}

    async def press(self, selector, key):
        return {"url": "http://x/", "shot": await self.screenshot()}

    async def back(self):
        return {"url": "http://x/", "shot": await self.screenshot()}

    async def scroll(self, selector="", direction="down", pixels=600):
        return {"url": "http://x/", "shot": await self.screenshot()}

    async def hover(self, selector):
        return {"url": "http://x/", "shot": await self.screenshot()}

    async def wait_for(self, selector="", text="", timeout_sec=15):
        if not selector and not text:
            raise BrowserError("wait_for needs a selector or text")
        return {"url": "http://x/", "found": True}


@pytest.fixture()
def registry():
    reg = ToolRegistry()
    fake = FakeSession()

    async def provider():
        return fake

    register_browser_tools(reg, provider)
    return reg, fake


def test_all_browser_tools_require_approval(registry):
    reg, _ = registry
    for spec in reg.specs():
        name = spec["name"]
        assert name.startswith("browser_")
        tool = reg.get(name)
        assert tool.requires_approval is True, name
        assert tool.risk == "high", name


async def test_open_and_screenshot_artifact(registry):
    reg, fake = registry
    result, receipt = await reg.call("browser_open", {"url": "http://example.com/"})
    assert result.ok is True
    assert result.artifacts["shot"].endswith(".png")
    assert receipt["tool"] == "browser_open"
    assert fake.opened == ["http://example.com/"]


async def test_snapshot_lists_elements(registry):
    reg, _ = registry
    result, _ = await reg.call("browser_snapshot", {})
    assert result.ok and "#search" in result.output


async def test_click_carries_shot(registry):
    reg, _ = registry
    result, _ = await reg.call("browser_click", {"selector": "#search"})
    assert result.ok is True
    assert "shot" in result.artifacts


def test_tool_args_validated(registry):
    reg, _ = registry
    with pytest.raises(ValueError):
        reg.validate("browser_fill", {"selector": "#q"})  # missing text


def test_scope_rejects_outside_domain():
    s = BrowserSession(allowed_domains=["example.com"])
    s._check_scope("https://example.com/a")
    s._check_scope("https://sub.example.com/b")
    with pytest.raises(BrowserError):
        s._check_scope("https://evil.com/")


def test_scope_rejects_non_http():
    s = BrowserSession()
    with pytest.raises(BrowserError):
        s._check_scope("file:///etc/passwd")


def test_scope_open_by_default():
    s = BrowserSession()
    s._check_scope("https://anything.example/")


def test_not_started_errors():
    s = BrowserSession()
    with pytest.raises(BrowserError):
        s._require_page()


async def test_scroll_carries_shot(registry):
    reg, _ = registry
    result, _ = await reg.call("browser_scroll", {"direction": "down", "pixels": 800})
    assert result.ok and "Scrolled" in result.output


async def test_hover_carries_shot(registry):
    reg, _ = registry
    result, _ = await reg.call("browser_hover", {"selector": "#menu"})
    assert result.ok and "Hovered" in result.output


async def test_wait_for_finds_text(registry):
    reg, _ = registry
    result, _ = await reg.call("browser_wait_for", {"text": "Buy now"})
    assert result.ok and "Found" in result.output


async def test_wait_for_needs_target(registry):
    reg, _ = registry
    result, _ = await reg.call("browser_wait_for", {})
    assert result.ok is False


def test_twenty_browser_tools_registered(registry):
    reg, _ = registry
    names = {s["name"] for s in reg.specs()}
    assert len(names) == 20
    assert {"browser_scroll", "browser_hover", "browser_wait_for",
            "browser_tab_new", "browser_tab_list",
            "browser_tab_switch", "browser_tab_close"} <= names
