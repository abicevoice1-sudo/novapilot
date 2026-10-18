"""Agent tool bindings for the browser workspace.

Every browser tool is risk=high AND requires_approval: the agent cannot move the
browser at all without the user's explicit approval. Actions use CSS selectors
from browser_snapshot; every action result carries a screenshot artifact.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from actlet_agent.tools import Tool, ToolResult
from pydantic import BaseModel, Field

APPROVAL_NOTE = (
    "Browser action. Requires your approval. Navigation is scoped to the "
    "allowed-domains list (empty = unrestricted)."
)


class _UrlArgs(BaseModel):
    url: str = Field(description="http(s) URL to open")


class _SelectorArgs(BaseModel):
    selector: str = Field(description="CSS selector from browser_snapshot")


class _FillArgs(BaseModel):
    selector: str = Field(description="CSS selector from browser_snapshot")
    text: str = Field(description="Text to type into the field")


class _SelectArgs(BaseModel):
    selector: str = Field(description="CSS selector from browser_snapshot")
    value: str = Field(description="Option value to choose")


class _PressArgs(BaseModel):
    selector: str = Field(description="CSS selector from browser_snapshot")
    key: str = Field(description="Key to press, e.g. Enter, Tab, Escape")


class _ShotArgs(BaseModel):
    label: str = Field(default="", description="Label for the screenshot")


class _ScrollArgs(BaseModel):
    selector: str = Field(default="", description="CSS selector of a scrollable element; empty = whole page")
    direction: str = Field(default="down", description="up or down")
    pixels: int = Field(default=600, ge=50, le=5000)


class _WaitArgs(BaseModel):
    selector: str = Field(default="", description="CSS selector to wait for (visible)")
    text: str = Field(default="", description="Text to wait for (alternative to selector)")
    timeout_sec: int = Field(default=15, ge=1, le=120)


class _TabIdArgs(BaseModel):
    tab_id: str = Field(description="Tab ID from browser_tab_list")


class _TabNewArgs(BaseModel):
    url: str = Field(default="", description="URL to open in the new tab (optional)")


class _NoArgs(BaseModel):
    pass


def _shot_artifacts(out: dict) -> dict:
    return {"shot": out["shot"]} if "shot" in out else {}


def register_browser_tools(registry, session_provider: Callable[[], Awaitable]) -> None:
    """session_provider: async callable returning a started BrowserSession."""

    async def _session():
        return await session_provider()

    async def browser_open(args: _UrlArgs) -> ToolResult:
        s = await _session()
        try:
            out = await s.open(args.url)
        except Exception as e:  # noqa: BLE001
            return ToolResult(ok=False, output=f"navigation blocked/failed: {e}")
        shot = await s.screenshot(label=f"open {out['url']}")
        return ToolResult(
            ok=True,
            output=f"Opened {out['url']} — {out['title']!r} (HTTP {out['status']}).",
            verification=f"screenshot {shot}",
            artifacts={"shot": shot},
        )

    async def browser_snapshot(args: BaseModel) -> ToolResult:
        s = await _session()
        items = await s.snapshot()
        lines = [f"<{it['role']}> {it['name']!r} -> {it['selector']}" for it in items]
        return ToolResult(
            ok=True,
            output="\n".join(lines) or "(no interactive elements)",
            verification=f"{len(items)} elements",
        )

    async def browser_read(args: BaseModel) -> ToolResult:
        s = await _session()
        out = await s.read()
        return ToolResult(ok=True, output=f"{out['title']} — {out['url']}\n{out['text']}")

    async def browser_click(args: _SelectorArgs) -> ToolResult:
        s = await _session()
        try:
            out = await s.click(args.selector)
        except Exception as e:  # noqa: BLE001
            return ToolResult(ok=False, output=str(e))
        return ToolResult(
            ok=True,
            output=f"Clicked {args.selector}. Now at {out['url']}.",
            verification=f"screenshot {out['shot']}",
            artifacts=_shot_artifacts(out),
        )

    async def browser_fill(args: _FillArgs) -> ToolResult:
        s = await _session()
        try:
            out = await s.fill(args.selector, args.text)
        except Exception as e:  # noqa: BLE001
            return ToolResult(ok=False, output=str(e))
        return ToolResult(
            ok=True,
            output=f"Filled {args.selector}.",
            verification=f"screenshot {out['shot']}",
            artifacts=_shot_artifacts(out),
        )

    async def browser_select(args: _SelectArgs) -> ToolResult:
        s = await _session()
        try:
            out = await s.select(args.selector, args.value)
        except Exception as e:  # noqa: BLE001
            return ToolResult(ok=False, output=str(e))
        return ToolResult(
            ok=True,
            output=f"Selected {args.value!r} in {args.selector}.",
            verification=f"screenshot {out['shot']}",
            artifacts=_shot_artifacts(out),
        )

    async def browser_press(args: _PressArgs) -> ToolResult:
        s = await _session()
        try:
            out = await s.press(args.selector, args.key)
        except Exception as e:  # noqa: BLE001
            return ToolResult(ok=False, output=str(e))
        return ToolResult(
            ok=True,
            output=f"Pressed {args.key!r} on {args.selector}.",
            verification=f"screenshot {out['shot']}",
            artifacts=_shot_artifacts(out),
        )

    async def browser_back(args: BaseModel) -> ToolResult:
        s = await _session()
        out = await s.back()
        return ToolResult(
            ok=True,
            output=f"Back to {out['url']}.",
            verification=f"screenshot {out['shot']}",
            artifacts=_shot_artifacts(out),
        )

    async def browser_screenshot(args: _ShotArgs) -> ToolResult:
        s = await _session()
        shot = await s.screenshot(label=args.label)
        return ToolResult(ok=True, output=f"Screenshot saved: {shot}", artifacts={"shot": shot})

    async def browser_scroll(args: _ScrollArgs) -> ToolResult:
        s = await _session()
        try:
            out = await s.scroll(args.selector, args.direction, args.pixels)
        except Exception as e:  # noqa: BLE001
            return ToolResult(ok=False, output=str(e))
        return ToolResult(
            ok=True,
            output=f"Scrolled {args.direction} {args.pixels}px.",
            verification=f"screenshot {out['shot']}",
            artifacts=_shot_artifacts(out),
        )

    async def browser_hover(args: _SelectorArgs) -> ToolResult:
        s = await _session()
        try:
            out = await s.hover(args.selector)
        except Exception as e:  # noqa: BLE001
            return ToolResult(ok=False, output=str(e))
        return ToolResult(
            ok=True,
            output=f"Hovered {args.selector}.",
            verification=f"screenshot {out['shot']}",
            artifacts=_shot_artifacts(out),
        )

    async def browser_wait_for(args: _WaitArgs) -> ToolResult:
        s = await _session()
        try:
            out = await s.wait_for(args.selector, args.text, args.timeout_sec)
        except Exception as e:  # noqa: BLE001
            return ToolResult(ok=False, output=str(e))
        target = args.selector or repr(args.text)
        return ToolResult(ok=True, output=f"Found {target} at {out['url']}.")

    async def browser_tab_new(args: _TabNewArgs) -> ToolResult:
        s = await _session()
        try:
            out = await s.tab_new(args.url)
        except Exception as e:  # noqa: BLE001
            return ToolResult(ok=False, output=str(e))
        return ToolResult(
            ok=True,
            output=f"Opened tab {out['tab_id']} ({out['url']}).",
            verification=f"screenshot {out['shot']}",
            artifacts=_shot_artifacts(out),
        )

    async def browser_tab_list(args: _NoArgs) -> ToolResult:
        s = await _session()
        tabs = await s.tab_list()
        lines = [
            f"{'*' if t['active'] else ' '} {t['tab_id']}: {t['title']!r} — {t['url']}"
            for t in tabs
        ]
        return ToolResult(ok=True, output="\n".join(lines) or "(no tabs)")

    async def browser_tab_switch(args: _TabIdArgs) -> ToolResult:
        s = await _session()
        try:
            out = await s.tab_switch(args.tab_id)
        except Exception as e:  # noqa: BLE001
            return ToolResult(ok=False, output=str(e))
        return ToolResult(
            ok=True,
            output=f"Switched to {out['tab_id']} ({out['url']}).",
            verification=f"screenshot {out['shot']}",
            artifacts=_shot_artifacts(out),
        )

    async def browser_tab_close(args: _TabIdArgs) -> ToolResult:
        s = await _session()
        try:
            out = await s.tab_close(args.tab_id)
        except Exception as e:  # noqa: BLE001
            return ToolResult(ok=False, output=str(e))
        return ToolResult(ok=True, output=f"Closed {out['closed']}; active is {out['active']}.")

    tools = [
        ("browser_open", "Open a URL in the agent browser (scoped navigation).", _UrlArgs, browser_open),
        ("browser_snapshot", "List interactive elements (buttons, links, inputs) with CSS selectors to use in actions.", _NoArgs, browser_snapshot),
        ("browser_read", "Read the visible text of the current page.", _NoArgs, browser_read),
        ("browser_click", "Click an element. Use a selector from browser_snapshot.", _SelectorArgs, browser_click),
        ("browser_fill", "Fill a text input. Use a selector from browser_snapshot.", _FillArgs, browser_fill),
        ("browser_select", "Choose an option in a dropdown.", _SelectArgs, browser_select),
        ("browser_press", "Press a key (e.g. Enter, Tab, Escape) on an element.", _PressArgs, browser_press),
        ("browser_scroll", "Scroll the page or an element up/down.", _ScrollArgs, browser_scroll),
        ("browser_hover", "Hover over an element (reveals menus).", _SelectorArgs, browser_hover),
        ("browser_wait_for", "Wait for an element or text to appear (dynamic pages).", _WaitArgs, browser_wait_for),
        ("browser_tab_new", "Open a new browser tab (optionally with a URL).", _TabNewArgs, browser_tab_new),
        ("browser_tab_list", "List open tabs with their URLs and titles.", _NoArgs, browser_tab_list),
        ("browser_tab_switch", "Switch to another tab.", _TabIdArgs, browser_tab_switch),
        ("browser_tab_close", "Close a tab (not the last one).", _TabIdArgs, browser_tab_close),
        ("browser_back", "Go back one page in history.", _NoArgs, browser_back),
        ("browser_screenshot", "Take a screenshot of the current page.", _ShotArgs, browser_screenshot),
    ]
    for name, desc, schema, fn in tools:
        registry.register(
            Tool(
                name,
                desc + " " + APPROVAL_NOTE,
                schema,
                fn,
                risk="high",
                requires_approval=True,
            )
        )
