---
name: job-search
description: Private, local-first job-search assistant that pulls live postings through the agent-data CLI, judges each one against the user's prose preferences (qualitative, no scores) and writes digests, ported from the Hermes job-search plugin, which is itself published as a Claude Code plugin. Use it when the user says "set up my job search", "I'm looking for a new job", "find me senior product design roles, remote", "run my job search now", "check for new jobs", "does this posting fit what I want", "why is this a strong match", "run my search every morning", or asks about their job-search digest, preferences brief or agent-data usage.
---
# Job Search

**Hermes original:** https://github.com/agent-data/job-search @ dba0c09 · tier: community · category: automation · license: MIT
**Port class:** A — the repository is a portable skills package with a `.claude-plugin/plugin.json` and seven `skills/*/SKILL.md`; the Hermes `__init__.py` only registers those skills. Install the upstream plugin in Claude Code directly; no MCP server is involved.

## What the Hermes plugin does
A `kind: standalone` plugin whose `register(ctx)` verifies the tree and registers seven skills: `job-search` (front door and home view), `job-search-run` (one headless search pass), `job-search-agent` (operator manual), `job-preference-interview` (writes the prose `preferences.md` brief), `evaluate-job-fit` (judges one posting as not relevant or weak/moderate/strong), `job-search-runbook` (workspace discovery, run contract) and `agent-data-reference` (the job-postings API). Postings come from the `agent-data` CLI, listing id `f9a6ec16-0bfd-44d8-b3ee-073776745ee7`, covering LinkedIn Jobs, Ashby, Greenhouse and Lever. Searches and posting reads go through the wrapper scripts `skills/job-search-run/scripts/search-jobs.sh` and `fetch-posting.sh`, which log every metered call to the workspace's `jobs.jsonl`. It registers no tools or hooks.

## Equivalent in Claude
Use the upstream plugin as published; the skills are written for Claude Code and run unchanged.

| Hermes skill | How Claude does it |
|---|---|
| `job-search:job-search` | `/job-search:job-search`, or say "Set up my job search. I'm looking for ..." |
| `job-search-run` | ask "run a search now" or let a scheduled task invoke the run skill |
| `job-preference-interview` | ask to define or change what you want in a job; writes `preferences.md` |
| `evaluate-job-fit` | paste a posting and ask whether it fits |
| `job-search-agent` | ask "how does my job search agent work" or "why did my last run fail" |
| `job-search-runbook`, `agent-data-reference` | internal; invoked by the other skills |

Workspace discovery (per `job-search-runbook`): the registry file is `$JOBSEARCH_OS_REGISTRY` when set, otherwise `${XDG_CONFIG_HOME:-${JOBSEARCH_OS_HOME:-$HOME}/.config}/job-search/config.json`; it names the active workspace holding `config.yaml`, `preferences.md`, `jobs.jsonl`, `runs/` and `reports/`. Direct agent-data commands the skills allow: `agent-data whoami`, `agent-data docs f9a6ec16-0bfd-44d8-b3ee-073776745ee7`, `agent-data init --api-key <KEY> -y`. All searching and posting reads must go through the two wrapper scripts so the run record counts every billable call.

Scheduling: the upstream skill installs `cron` or `launchd` jobs. In Claude Code you can instead create a scheduled task that sends "run my job search now" into a session; the digest lands in the workspace's `reports/` directory.

## Setup
1. In Claude Code run `/plugin marketplace add agent-data/job-search` then `/plugin install job-search@agent-data` (per the README). Other listed agents: Codex, Cursor, opencode, Gemini CLI, Copilot CLI, Factory Droid, Pi.
2. Install the data CLI: `npm install -g agent-data` (verified with `npm view agent-data`: version 0.14.0, "CLI tool for agents to discover and explore agent-data marketplace APIs").
3. Create an agent-data API key and run `agent-data init --api-key <KEY> -y`; the key is stored in `~/.agent-data/config.json`. The skill walks through this during onboarding.
4. Optional environment variables: `JOBSEARCH_OS_REGISTRY`, `JOBSEARCH_OS_HOME`, `XDG_CONFIG_HOME` to relocate the registry and workspace.

## Limits
- Metered third-party service: agent-data offers 100 free calls per month, then calls are refused with `403 insufficient_credits`; a typical run spends about 10 to 30 calls per the README. The skills state the expected cost before searching. Billing page: https://agent-data.motie.dev/settings/billing.
- Posting content and your preferences brief are sent to the agent-data API only as search parameters; the brief itself stays local, but postings fetched are third-party data and the skills treat them as untrusted.
- Judgments run on whatever model the session uses; results differ between runs.
- Sources are limited to LinkedIn Jobs, Ashby, Greenhouse and Lever at the reviewed commit.
- Not verified here: the wrapper scripts and evals were read, not executed.

## Source
- Catalog entry (reviewed commit): https://github.com/agent-data/job-search/tree/dba0c0992e9d7fc6533dd1be3003df7a311168f0
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/job-search.yaml
- Upstream skills (MIT) copied under `references/`: `upstream-job-search.md`, `upstream-job-search-run.md`, `upstream-job-search-agent.md`, `upstream-job-preference-interview.md`, `upstream-evaluate-job-fit.md`, `upstream-job-search-runbook.md`, `upstream-agent-data-reference.md`. They reference sibling `scripts/` and `templates/` that live in the upstream repository, not in this pack.
