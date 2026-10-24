"""Multi-browser context tests: new/list/switch/close, isolation."""

import pytest

from actlet_browser.session import BrowserSession


@pytest.fixture()
async def session(tmp_path):
    s = BrowserSession(shots_dir=str(tmp_path / "shots"))
    await s.start()
    yield s
    await s.close()


async def test_starts_with_main_context(session):
    ctxs = await session.context_list()
    assert len(ctxs) == 1
    assert ctxs[0]["context_id"] == "main"
    assert ctxs[0]["active"] is True
    assert len(ctxs[0]["tabs"]) == 1


async def test_context_new_and_switch(session):
    out = await session.context_new("user2")
    assert out["context_id"] == "user2"
    ctxs = await session.context_list()
    assert len(ctxs) == 2
    assert any(c["active"] and c["context_id"] == "user2" for c in ctxs)
    # switch back to main
    out = await session.context_switch("main")
    assert out["context_id"] == "main"
    ctxs = await session.context_list()
    assert any(c["active"] and c["context_id"] == "main" for c in ctxs)


async def test_context_tabs_isolated(session):
    await session.context_new("user2")
    await session.tab_new()  # tab in user2 context
    ctxs = await session.context_list()
    main = next(c for c in ctxs if c["context_id"] == "main")
    user2 = next(c for c in ctxs if c["context_id"] == "user2")
    assert len(main["tabs"]) == 1
    assert len(user2["tabs"]) == 2


async def test_context_close(session):
    await session.context_new("user2")
    out = await session.context_close("user2")
    assert out["closed"] == "user2"
    assert out["active"] == "main"
    ctxs = await session.context_list()
    assert len(ctxs) == 1


async def test_cannot_close_last_context(session):
    with pytest.raises(Exception, match="last browser context"):
        await session.context_close("main")


async def test_switch_unknown_context(session):
    with pytest.raises(Exception, match="no such browser context"):
        await session.context_switch("nope")


async def test_duplicate_context_name(session):
    await session.context_new("user2")
    with pytest.raises(Exception, match="already exists"):
        await session.context_new("user2")
