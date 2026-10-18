"""Browser tab tests: new/list/switch/close."""

import pytest

from actlet_browser.session import BrowserSession


@pytest.fixture()
async def session(tmp_path):
    s = BrowserSession(shots_dir=str(tmp_path / "shots"))
    await s.start()
    yield s
    await s.close()


async def test_starts_with_one_tab(session):
    tabs = await session.tab_list()
    assert len(tabs) == 1
    assert tabs[0]["active"] is True
    assert tabs[0]["tab_id"] == "tab-1"


async def test_tab_new_and_switch(session):
    out = await session.tab_new()
    assert out["tab_id"] == "tab-2"
    tabs = await session.tab_list()
    assert len(tabs) == 2
    assert any(t["active"] and t["tab_id"] == "tab-2" for t in tabs)
    # switch back
    out = await session.tab_switch("tab-1")
    assert out["tab_id"] == "tab-1"
    tabs = await session.tab_list()
    assert any(t["active"] and t["tab_id"] == "tab-1" for t in tabs)


async def test_tab_new_with_blank(session):
    out = await session.tab_new()
    assert out["tab_id"] == "tab-2"
    assert out["url"] == "about:blank"


async def test_tab_close(session):
    await session.tab_new()
    out = await session.tab_close("tab-2")
    assert out["closed"] == "tab-2"
    tabs = await session.tab_list()
    assert len(tabs) == 1


async def test_cannot_close_last_tab(session):
    with pytest.raises(Exception, match="last tab"):
        await session.tab_close("tab-1")


async def test_switch_unknown_tab(session):
    with pytest.raises(Exception, match="no such tab"):
        await session.tab_switch("tab-99")
