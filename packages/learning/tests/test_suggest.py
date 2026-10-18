"""Dreaming schedule-suggestion tests: proposals from recurring patterns."""

import json
from unittest.mock import AsyncMock

from actlet_learning.dream import DreamConsolidator


def _gateway(payload):
    g = AsyncMock()
    g.chat.return_value = json.dumps(payload)
    return g


def _memory():
    return AsyncMock()


async def test_proposes_schedule_for_recurring_task():
    g = _gateway([
        {"name": "friday flight check", "goal": "Check flight prices to Chicago",
         "cadence": "every Friday at 6pm"},
    ])
    c = DreamConsolidator(g, _memory())
    tasks = [
        {"goal": "Check flight prices to Chicago", "summary": "found $220"},
        {"goal": "Check flight prices to Chicago again", "summary": "found $205"},
    ]
    proposals = await c.suggest_schedules(tasks)
    assert len(proposals) == 1
    p = proposals[0]
    assert p["goal"] == "Check flight prices to Chicago"
    assert p["cadence"] == "every Friday at 6pm"
    assert p["source"] == "dreaming"


async def test_empty_for_one_off_tasks():
    g = _gateway([])
    c = DreamConsolidator(g, _memory())
    proposals = await c.suggest_schedules([{"goal": "Book a dentist"}])
    assert proposals == []


async def test_skips_items_missing_fields():
    g = _gateway([{"name": "vague"}, {"goal": "Real goal", "cadence": "daily"}])
    c = DreamConsolidator(g, _memory())
    proposals = await c.suggest_schedules([{"goal": "Real goal"}])
    assert len(proposals) == 1
    assert proposals[0]["goal"] == "Real goal"


async def test_bad_model_output_returns_empty():
    g = AsyncMock()
    g.chat.return_value = "not json at all"
    c = DreamConsolidator(g, _memory())
    proposals = await c.suggest_schedules([{"goal": "Check weather"}])
    assert proposals == []


async def test_no_goals_returns_empty():
    g = _gateway([])
    c = DreamConsolidator(g, _memory())
    assert await c.suggest_schedules([]) == []
    assert await c.suggest_schedules([{"summary": "no goal"}]) == []
