---
name: health-data
description: Answer personal health and daily-context questions (sleep, readiness, recovery, stress, HRV, resting heart rate, SpO2, workouts, steps, food logs, and how meetings or inbox load line up with them) from the user's Oura ring data pulled over the Oura v2 REST API, combined with Google Calendar and Gmail metadata, following the health-coach answering loop ported from the Hermes "health-data" (Apollo) plugin. Use when the user asks "how did I sleep", "why was I stressed yesterday", "am I recovered enough to train", "did my meetings line up with my stress", "what changed in my baseline", "log this meal", or wants a terminal-style health visual. Not for medical diagnosis.
---
# Health Data (Oura + calendar context coach)

**Hermes original:** https://github.com/Infinite-Labs-AI/hermes-health-apollo @ 9f2db67 · tier: community · category: tools · license: MIT
**Port class:** C — the Oura REST pulls, the Google Calendar/Gmail context and the coaching rules are reproducible; the local SQLite store, feature engineering, analysis plans, `hermes health` CLI and 6-hourly sync cron are Hermes-internal.

## What the Hermes plugin does
A `standalone` plugin that syncs Oura data into `~/.hermes/health.db`, pulls redacted Google Calendar and Gmail metadata through the Hermes Google Workspace helper, and registers 11 tools: `health_query` (recent, date_range, stress_days, correlate, heart_rate, workouts, sessions, tags, coverage), `health_sync`, `health_log_food`, `health_calendar_peek`, `health_coverage`, `health_event_query`, `health_feature_query`, `health_analysis_catalog`, `health_analysis_plan`, `health_analyze`, `health_analysis_explain`. It adds a `/health` command family (`hermes health setup|connect|connect-google|sync|status|ask|uninstall`), a `health-data-sync` cron every 6 h, and two skills: `health-coach` (answering loop, correlation recipe, guardrails) and `health-visuals` (terminal-only visual patterns).

## Equivalent in Claude
1. Coaching behavior: follow `references/upstream-health-coach.md` (answer loop, compare to the user's own baseline, hedge with "likely" and "associated with", no diagnosis, escalate sustained SpO2 under about 90 percent or acute symptoms). For chart or dashboard requests follow `references/upstream-health-visuals.md` and render plain-text visuals.
2. Oura data (per `oura.py`): the user needs an OAuth access token for their own Oura developer app (`HERMES_OURA_CLIENT_ID`, `HERMES_OURA_CLIENT_SECRET`; authorize at `https://cloud.ouraring.com/oauth/authorize`, token at `https://api.ouraring.com/oauth/token`, redirect URI `http://localhost:43828/callback`). Claude Code cannot complete the browser consent itself; ask the user to obtain the token (or a personal access token from the Oura cloud portal) and export it, then query:

```bash
curl -sS "https://api.ouraring.com/v2/usercollection/daily_sleep?start_date=2026-11-01&end_date=2026-11-20" \
  -H "Authorization: Bearer $OURA_ACCESS_TOKEN"
```

   Endpoints the plugin syncs (all under `https://api.ouraring.com`): `/v2/usercollection/daily_sleep`, `daily_readiness`, `daily_stress`, `daily_activity`, `daily_spo2`, `sleep`, `workout`, `session`, `tag`, `enhanced_tag`, `daily_resilience`, `daily_cardiovascular_age`, `vO2_max`, `sleep_time`, `rest_mode_period`, `heartrate` (datetime window), `ring_battery_level`, `ring_configuration`, `personal_info`. Paginate with `next_token`. Backfill once with a wide range, then use short rolling windows.
3. Calendar and inbox context: use the Claude Google Calendar and Gmail connectors when connected (list events and message counts per day); store only counts, durations and titles the user agrees to, never bodies.
4. Correlation recipe (from the skill): same-day joins for stress vs meetings/email/activity/food; shifted joins for sleep night N vs readiness day N+1; frame as associations. Say when coverage is thin.
5. Food logging: when the user describes or photographs a meal, extract items and an estimated total, keep it in a local file the user names (for example `~/health/food_log.jsonl`), and never invent calories if parsing fails.

| Hermes tool | How Claude does it |
|---|---|
| `health_sync` | curl the Oura endpoints above into local JSON/CSV files |
| `health_query` recent / date_range / heart_rate / workouts | Filter the fetched JSON with python or jq |
| `health_calendar_peek` | Google Calendar connector list_events |
| `health_coverage` | Report which endpoints returned rows for the window |
| `health_analysis_plan` / `health_analyze` / `_explain` | Reason in chat following the correlation recipe; show the data used |
| `health_log_food` | Append to a user-chosen local file |

## Setup
1. Create an Oura developer app at `https://cloud.ouraring.com/oauth/applications` (scopes per README: Daily, Session, SpO2, Stress, Heartrate, Tag, Workout, Personal, Heart Health, Ring Configuration) and obtain an access token; export it as `OURA_ACCESS_TOKEN` (name chosen for this port; the plugin stored its token in a file, not an env var).
2. Optionally connect the Google Calendar and Gmail connectors in Claude.

## Limits
- No persistent local database, feature registry, analysis catalog or provenance tables; each session re-fetches data.
- No scheduled sync; the 6-hourly `health-data-sync` cron was a Hermes gateway job.
- OAuth loopback flow, token refresh and the `hermes health` CLI are not replicated; the user supplies a valid token.
- Health data is sensitive PII. Keep files local, do not paste raw exports into shared artifacts, and respect the plugin's rule of not storing Gmail bodies or attendee identities.
- Not verified against a live Oura account; endpoint paths are copied from the plugin source.

## Source
- Catalog entry (reviewed commit): https://github.com/Infinite-Labs-AI/hermes-health-apollo/tree/9f2db670a2669c9f3401fecb3b547ed52bcb2c3b
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/health-data.yaml
