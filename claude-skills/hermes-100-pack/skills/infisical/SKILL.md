---
name: infisical
description: Read secrets from an Infisical secret store (US/EU cloud or self-hosted) over its REST API and turn them into environment variables for a shell or process, replicating the Hermes infisical secret-source plugin. Use it when the user says "pull my API keys from Infisical", "resolve inf://project/env/folder/KEY", "export everything in the prod backend folder from Infisical", "log in to Infisical with a machine identity", "create a dynamic secret lease", or wants provider credentials kept out of plaintext .env files. Uses the same env vars as the plugin (INFISICAL_TOKEN, INFISICAL_CLIENT_ID, INFISICAL_CLIENT_SECRET). Read-only; never writes secrets back.
---
# Infisical secret source

**Hermes original:** https://github.com/antonba/hermes-infisical-plugin @ d1c5d46 · tier: community · category: general · license: no LICENSE file found
**Port class:** B · the plugin is a thin client over documented Infisical REST endpoints (listed in `infisical_plugin/client.py`); Claude can call them with curl and export the results.

## What the Hermes plugin does
Registers two Hermes secret sources, not tools: `infisical` (mapped: `ENV_VAR: inf://<project>/<environment>[/<folder>...]/<key>[?type=dynamic&field=...&ttl=...]`) and `infisical_bulk` (inject a whole project/environment/folder). At Hermes startup it authenticates by one of three methods (`agent` token file, default `~/.infisical/agent-token`; `universal-auth` machine identity; static `token`), resolves project names/slugs to IDs, fetches secret values, and places them in the Hermes process environment. Strictly read-only; dynamic-secret leases are created once at startup and never renewed. `INFISICAL_TOKEN`, `INFISICAL_CLIENT_ID`, `INFISICAL_CLIENT_SECRET` are protected from being overwritten.

## Equivalent in Claude
Host default from source: `https://us.infisical.com` (EU or self-hosted hosts are set per config). All requests send `Authorization: Bearer $TOKEN`; TLS verification stays on. Never echo secret values into chat; write them to a 0600 env file and tell the user the file path.

1. Obtain a token (same precedence as the plugin config `auth.method`):
   - `agent`: `TOKEN=$(cat ~/.infisical/agent-token)` (the Infisical Agent's file sink).
   - `universal-auth`: `curl -s -X POST "$HOST/api/v1/auth/universal-auth/login" -H 'Content-Type: application/json' -d "{\"clientId\":\"$INFISICAL_CLIENT_ID\",\"clientSecret\":\"$INFISICAL_CLIENT_SECRET\"}"` and read `.accessToken`. Credentials may also come from files named by `client_id_path` / `client_secret_path`.
   - `token`: `TOKEN=$INFISICAL_TOKEN`.
2. Resolve a project name or slug to its ID: `GET $HOST/api/v1/projects` -> match `projects[]` by `name`, `slug` or `id`. A UUID can be used directly.
3. One secret (mapped `inf://` reference): `GET "$HOST/api/v4/secrets/<urlencoded key>?projectId=<id>&environment=<env>&secretPath=</folder>&viewSecretValue=true&expandSecretReferences=true&includeImports=true"` -> `.secret.secretValue`.
4. A whole folder (bulk): `GET "$HOST/api/v4/secrets?projectId=<id>&environment=<env>&secretPath=</folder>&recursive=false&includeImports=true&viewSecretValue=true&expandSecretReferences=true"` -> `.imports[].secrets[]` first, then `.secrets[]` (direct secrets override imports), each with `secretKey` and `secretValue`. The v4 list route has no pagination per the source.
5. Dynamic secret (`?type=dynamic&field=<f>&ttl=<d>`): `POST $HOST/api/v1/dynamic-secrets/leases` with `{"dynamicSecretName":"<key>","projectSlug":"<slug>","environmentSlug":"<env>","path":"</folder>","ttl":"8h"}` -> `.data`; pick `field` when the payload has more than one.
6. Write `export NAME='value'` lines to a file (`umask 077`), then the user runs `source` on it or passes it to the target process.

| Hermes config / source | How Claude does it |
|---|---|
| `secrets.infisical.env: {VAR: inf://...}` | parse the reference, steps 2-3 (or 5), export VAR |
| `secrets.infisical_bulk` (`project`, `environment`, `secret_path`, `recursive`, `include_imports`) | step 4 with those query values |
| `override_existing` | ask before overwriting a var already set in the target env file |
| `timeout_seconds` (120) / per-call 30 s | `curl --max-time 30` |
| HTTP 401 | report `auth_failed`, stop; do not retry with other methods silently |

Alternative client: `infisicalsdk` 1.4.1 exists on PyPI (verified with `pip index versions infisicalsdk`); its API surface was not checked here, so prefer the curl calls above, which are copied from the plugin.

## Setup
1. Have an Infisical server exposing the v4 secrets API (Infisical Cloud or a recent self-hosted release, per README).
2. Choose an auth method: run the Infisical Agent with a file sink, or create a Machine Identity and `export INFISICAL_CLIENT_ID=... INFISICAL_CLIENT_SECRET=...`, or `export INFISICAL_TOKEN=...`.
3. Know the project (name, slug or ID), environment slug and folder path for each secret.

## Limits
- Startup injection into a long-running agent process is Hermes-specific; Claude produces an env file or exports for a subprocess instead.
- Lease renewal for dynamic secrets is not done by the plugin and is not done here.
- No write-back (creating or updating secrets) by design.
- Secrets fetched are sensitive; keep them out of chat, logs and shell history (`set +o history` before `export`, or use the env file).
- No LICENSE file at the reviewed commit, so no upstream text is copied; endpoints above are restated facts from `client.py` and `auth.py`.
- No upstream skills/ directory exists.

## Source
- Catalog entry (reviewed commit): https://github.com/antonba/hermes-infisical-plugin/tree/d1c5d46267bcc05f1ee2ae68e06f0ba3072d656a
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/infisical.yaml
