# nano-muse/nanoMuse

- **Canonical URL:** https://github.com/nano-muse/nanoMuse (no redirect observed)
- **Category:** Open-source personal AI agent for every device you own (Android/iOS/desktop/browser).

**Verification date:** 2026-10-18. Stats from saved API JSON: stars **1399**, forks **154**, open issues **55**, license **GPL-3.0** (README says GPL-3.0-or-later), primary language **Swift** (API-reported; repo also holds phone/desktop/web components), last push **2026-10-18T03:43:11Z**, archived: **no**. Latest release: **v1.0.5 "Lookout"** (verified in README; 1.0.0 "Keel" shipped 2026-10-09; first release 2026-09-25, 1k stars in 18 days). arXiv paper 2610.08699 (2026-10-07).

## Models / free / local / BYOK
- Sign-in gives a **free allowance of model use on the community relay** (developer pays); when exhausted, use your own key (docs/own-key.md).
- **BYOK:** 21 providers (Bailian, OpenRouter, OpenAI, Gemini, DeepSeek, etc.), plus "use a plan you already pay for" (ChatGPT, Claude, Kimi). Provider without image/video models simply loses those features, and the app says so.
- **Local:** phone agent built on OpenMinis 1.13; fully self-hostable relay (`scripts/self-host.sh`) so "nothing has to leave your house".

## Memory
- Markdown files: "What it is, what it knows about you and when it wakes are Markdown files you can read and edit." Persistent, user-inspectable/editable.

## Proactive / scheduling / background / goals
- "Keeps going": goals checked on a schedule, routines that run **while the app is closed**, a feed written for the user each morning. Multi-device orchestration: `@Mac …` sends a task to another device; approvals return to the device in hand.

## Browser / computer / files / terminal
- A Linux shell (Alpine under proot on phone), a browser, MCP servers, skills; **Hands**: screen-based control of phone apps and computer windows (screenshots, APIs first, human takes over for logins/CAPTCHA). Not on iOS (OS disallows it).

## Integrations / APIs / plugins / MCP / messaging
- MCP servers, skills; lives in 飞书, 钉钉, 企业微信 and Telegram. Relay hub joins all devices on one account.

## Multi-agent
- None in the classical sense; devices ask each other for things over the hub — device-federated, not subagent orchestration.

## Voice / image / documents / multimodal
- Image model draws its avatar, video model animates it (default: small dragon). Image/video only via providers that support them.

## Install / hardware / cost / maintenance
- Install: one-line per platform — APK (Android 8+), TestFlight (iOS), DMG (macOS), exe (Windows), AppImage/deb/tar (Linux), Docker, browser demo. Self-host: "one VPS, one hour". Maintenance burden: young project, releases every few days; roadmap in docs/roadmap.md.

## Security / privacy
- **Asks-first**: a stop before deleting, sending or paying, remembered per scope (once / this chat / always); passwords and codes are typed by the user, never the agent. Logins/CAPTCHAs handed to the human; "Done" resumes. Self-hostable relay; conversations travel through the relay, files/screenshots stay on-device.

## Top 3 strengths
1. Device-federated architecture: one account across phone/desktop/web, tasks and approvals routed between devices.
2. Screen-as-hands device control (phone + desktop), honest about limits (not on iOS).
3. Free community relay allowance + full self-host + BYOK = genuinely usable without a paid subscription.

## Top 3 weaknesses
1. Extremely young (3 weeks, v1.0.5); longevity and real-world robustness unverified.
2. GPL-3.0-or-later copyleft is a constraint for commercial embedding and for us if we wanted to borrow code.
3. Account sign-in + China-centric options (mainland phone) and dev-funded relay — trust/cost model depends on maintainer funding.

## Best lesson to steal
**Approvals follow the user across devices** — the interruption is delivered to the device in the user's hand, and screen-based hands with graceful handoff to the human for logins/CAPTCHAs.

## Scores (1–10, evidence)
1. Intelligence/model flexibility: **8** — 21 providers + paid-plan reuse + relay allowance; local OpenMinis.
2. Persistent memory: **7** — user-readable/editable Markdown memory files.
3. Autonomous execution: **7** — works while app closed; but human takeover required for logins.
4. Proactive assistance: **6** — scheduled goal checks, morning feed; budget/quiet-hour detail unknown.
5. Browser/computer control: **8** — browser + shell + screen-hands on phone/desktop.
6. Integrations/extensibility: **7** — MCP, skills, 4 chat apps; plugin SDK depth unknown.
7. Privacy/security: **7** — asks-first with remembered scope, self-hostable; relay operator can see conversations.
8. Ease of deployment: **9** — per-platform binaries, Docker, one-hour self-host.
9. Free-tier/local accessibility: **8** — free relay allowance + self-host; allowance is dev-funded, not guaranteed.
10. Reliability/observability: **5** — 3-week-old project, CI exists, real-world record thin.
11. User experience: **8** — named agent with a look, chat apps, polished install matrix.
12. Community health: **5** — 1.4k stars fast, Discord, but small maintainer team (ZJU), GPL.

## Verdict
**Active** (pushed today, releases every few days). Keep — the device-federation model is the strongest idea in this batch. Replacement if dropped: openclaw/openclaw (gateway+channels) or NousResearch/hermes-agent (maturity).
