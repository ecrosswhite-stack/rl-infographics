---
name: hermes-plugin-netbox
description: "Read and change objects in a NetBox DCIM/IPAM instance through its REST API using the user's NETBOX_URL and NETBOX_TOKEN, following the plan, review, apply, roll back discipline of the Hermes netbox plugin: never write without first showing a field-level diff and getting a yes. Use when the user asks to look up, add, move, rename, retire, re-IP or bulk-edit devices, interfaces, IP addresses, prefixes, sites, racks, circuits or VMs in NetBox, says \"query netbox\", \"plan this netbox change\", \"apply the plan\", or \"roll back that netbox change\"."
---
# NetBox Change Management

**Hermes original:** https://github.com/andrewvieyra/hermes-plugin-netbox @ 8ff1fc4 · tier: community · category: tools · license: MIT
**Port class:** B · a REST client for NetBox plus plan/journal logic; Claude can call the same API with curl and keep the plan and journal as JSON files itself.

## What the Hermes plugin does
Registers five tools: `netbox_query` (list with filters, fetch by id, `status`), `netbox_plan` (validate operations, resolve `match` to one object, diff desired vs live, save a plan with each object's `last_updated`), `netbox_apply` (re-check `last_updated`, POST/PATCH/DELETE step by step, journal an inverse before the next step, auto-rollback on failure), `netbox_rollback` (replay the journal newest first) and `netbox_plans`. Plans live under `~/.hermes/plugin-data/netbox/plans/`, events in `audit.jsonl`. Settings: `allow_delete` (default false), `max_operations` 200, `max_plan_age_hours` 24, `write_mode` full/operator_only/read_only. It ships a `netbox-workflow` skill (copied to `references/`).

## Equivalent in Claude
Per `client.py`: base is `$NETBOX_URL/api/<endpoint>/`; header `Authorization: Token $NETBOX_TOKEN`, or `Authorization: Bearer $NETBOX_TOKEN` when the token starts with `nbt_`; `Accept: application/json`; `NETBOX_VERIFY_SSL=false` disables certificate checks; `NETBOX_TIMEOUT` default 30 s. Endpoints are paths relative to `/api/` such as `dcim/devices`, `ipam/prefixes`, `extras/journal-entries`.

```bash
auth() { case "$NETBOX_TOKEN" in nbt_*) echo "Bearer $NETBOX_TOKEN";; *) echo "Token $NETBOX_TOKEN";; esac; }
curl -sS "$NETBOX_URL/api/dcim/devices/?name=sw1&brief=1" -H "Authorization: $(auth)" -H "Accept: application/json"
```

Procedure (from `references/upstream-netbox-workflow.md`):
1. Query first. Resolve every related object (site, role, device type, tenant, VRF, tags) to an integer id with filters like `?slug=nyc` or `?name__ic=core`. Follow `next` for pagination; stop at 500 objects.
2. Build a plan file `netbox-plans/nbp-<UTC timestamp>.json` with `description`, ordered `operations` (`{"op": "create|update|delete", "endpoint": ..., "id" | "match": {...}, "data": {...}}`), and for each target the live object, its `last_updated`, and the computed diff (only keys present in `data`). A `match` must hit exactly one object. `create` with `match` that finds an object becomes `update` or `noop`.
3. Show the diff verbatim and ask "Apply plan <id>? yes/no". Wait. In an unattended run, do not apply.
4. Apply in order: GET the object again, abort if `last_updated` changed; `POST` for create, `PATCH` with only the differing fields for update, `DELETE` only if the user enabled deletes. Before the next step, append the inverse to the plan's `journal` (delete the created id; PATCH the previous values; re-create from the snapshot). On failure, run the journal in reverse and report.
5. Verify by querying the touched objects. Offer rollback by replaying the journal newest first, skipping objects edited since apply unless the user accepts overwriting.
6. `data` rules: related objects as ids or lookup dicts (`{"slug": "nyc"}`), choice values not labels, tags as the full desired list, `custom_fields` partial.

| Hermes tool | How Claude does it |
|---|---|
| `netbox_query` | `curl GET $NETBOX_URL/api/<endpoint>/?<filters>` |
| `netbox_plan` | Query, diff and write the plan JSON locally |
| `netbox_apply` | Re-check, then POST/PATCH/DELETE step by step, journaling inverses |
| `netbox_rollback` | Replay the journal in reverse |
| `netbox_plans` | List or cat the local plan files |

Optional read-only MCP server, verified with `pip index versions netbox-mcp-server`: output `netbox-mcp-server (1.3.0)`; PyPI summary "A read-only MCP server for NetBox", homepage github.com/netboxlabs/netbox-mcp-server. It covers reads only; writes still follow the procedure above.

## Setup
1. Create a NetBox API token scoped to the permissions the agent should have (a read-only token is the one safeguard NetBox enforces itself).
2. `export NETBOX_URL=https://netbox.example.com` and `export NETBOX_TOKEN=...`; optionally `NETBOX_VERIFY_SSL=false`, `NETBOX_TIMEOUT=30`.

## Limits
- The plan lock, plan expiry, `write_mode` enforcement, audit sinks (syslog, Splunk HEC) and NetBox change-log linking were Python guarantees; here they are procedure Claude must follow, not a lock.
- Deletes cascade in NetBox and a rollback re-creates with a new id; keep deletes off unless asked.
- The `/netbox` slash command and `hermes netbox` CLI are not replicated.
- Every write changes production inventory data on the user's NetBox; always confirm first.

## Source
- Catalog entry (reviewed commit): https://github.com/andrewvieyra/hermes-plugin-netbox/tree/8ff1fc408e765294664e6ed96c4a5a437b76ceef
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/hermes-plugin-netbox.yaml
