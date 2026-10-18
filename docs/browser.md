# Browser workspace — safety model

Nova drives a real Chromium (Playwright, headless). The browser is powerful,
so it is gated harder than any other tool.

## Rules (enforced in code, not prompts)

1. **Every browser action requires approval.** `browser_open`, `browser_click`,
   `browser_fill`, `browser_select`, `browser_press`, `browser_back`,
   `browser_snapshot`, `browser_read`, `browser_screenshot` are all `risk=high`
   + `requires_approval`. The agent cannot move the mouse at all until you
   approve the step. Deny once and the step is skipped.
2. **Scoped navigation.** `BROWSER_ALLOWED_DOMAINS` (comma-separated) restricts
   which hosts the browser may visit; anything else is rejected before the
   request leaves the box. Empty = unrestricted (local dev default).
   Only `http(s)` URLs — no `file://`, no custom schemes.
3. **Audit trail.** Every action emits a tool receipt (tool, args digest,
   duration, outcome) into the task's event stream, plus a screenshot artifact.
   Screenshots are served at `GET /api/shots/{name}` (traversal-proof).
4. **No credential autofill.** Nova never fills passwords and never reads saved
   logins. If a site needs sign-in, the approval card says so and you sign in
   yourself — or deny the step.

## What the agent can do

Open pages, list interactive elements (`browser_snapshot` returns CSS selectors),
click, fill forms, select dropdowns, press keys, read page text, screenshot.
Multi-step flows (search → results → details) work through the normal
plan → approve → execute → verify loop; a failed selector returns the error
plus a fresh snapshot so the agent can retry.

## Setup

`pip install playwright && playwright install chromium` (the Docker image does
this at build time). Chromium starts lazily on first browser tool use, not at
API boot. Screenshots land in `<workspace>/browser-shots/`.
