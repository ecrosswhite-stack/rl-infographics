---
name: s3
description: Back up files or directory trees to any S3-compatible object store (AWS S3, Cloudflare R2, MinIO) and list, restore or safely delete remote objects, replicating the Hermes s3 plugin's s3-push, s3-pull, s3-ls and s3-rm tools with boto3 or the aws CLI. Use it when the user says "push this folder to my bucket", "back up ~/project to S3 under backups/{date}", "restore builds/latest into ./restored", "list objects under backups/", "delete that old backup from R2", or references S3_BACKUP_* variables or a named rule from s3-backup.rules.yaml. Push skips existing objects unless forced; delete always requires explicit confirmation.
---
# S3 backup and restore

**Hermes original:** https://github.com/lagoon-labs/hermes-s3-plugin @ 3d1514e · tier: community · category: tools · license: MIT
**Port class:** B · a boto3 wrapper configured entirely by env vars; Claude can run the same boto3 calls (or the aws CLI) directly.

## What the Hermes plugin does
Registers four tools in toolset `s3`: `s3-push` (args `src|local`, `dst|remote`, `rule`, `force`), `s3-pull` (`src|remote`, `dst|local`, `rule`), `s3-ls` (`prefix`, `rule`), `s3-rm` (`key` or `prefix`, `rule`, `recursive`, `confirm`), plus a `hermes s3 push|pull|ls|rm` CLI. Config comes from `S3_BACKUP_ENDPOINT` (omit for AWS), `S3_BACKUP_REGION`, `S3_BACKUP_BUCKET`, `S3_BACKUP_ACCESS_KEY`, `S3_BACKUP_SECRET_KEY`, `S3_BACKUP_RULES` (default `~/.hermes/s3-backup.rules.yaml`). Named rules supply `prefix` (with `{date}`, `{ts}`, `{year}`, `{month}`, `{day}` UTC placeholders) and an optional relative `source`. Push skips objects that already exist unless `force`; pull validates destination paths including symlink resolution; rm requires `confirm` and, for a prefix, `recursive`. All results are JSON (`{"ok": true, ...}`).

## Equivalent in Claude
boto3 1.44.8 is on PyPI (verified with `pip index versions boto3`). Build the client exactly as `storage.py` does:

```bash
python3 -I - <<'PY'
import boto3, os
s3 = boto3.client("s3", endpoint_url=os.environ.get("S3_BACKUP_ENDPOINT") or None,
    region_name=os.environ.get("S3_BACKUP_REGION"),
    aws_access_key_id=os.environ["S3_BACKUP_ACCESS_KEY"],
    aws_secret_access_key=os.environ["S3_BACKUP_SECRET_KEY"])
# then list_objects_v2 / upload_file / download_file / delete_object as needed
PY
```

With the aws CLI instead (if installed): `AWS_ACCESS_KEY_ID=$S3_BACKUP_ACCESS_KEY AWS_SECRET_ACCESS_KEY=$S3_BACKUP_SECRET_KEY AWS_DEFAULT_REGION=$S3_BACKUP_REGION aws s3 ... ${S3_BACKUP_ENDPOINT:+--endpoint-url $S3_BACKUP_ENDPOINT}`.

| Hermes tool | How Claude does it |
|---|---|
| `s3-ls prefix=` | `list_objects_v2(Bucket, Prefix)` following `NextContinuationToken`; print Key, Size, LastModified |
| `s3-push src= dst= [force]` | walk the local path (`os.walk`, no symlink following); for each file compute `dst/<relative path>` (a single file keeps its name); skip keys that already exist unless force; `upload_file` |
| `s3-pull src= dst=` | list the prefix; for each key build `dst/<key minus prefix>`; reject absolute, `..` or symlink-escaping paths; `download_file` |
| `s3-rm key= confirm=true` | `delete_object(Bucket, Key)` only after the user confirmed that exact key |
| `s3-rm prefix= recursive=true confirm=true` | list then delete each key; refuse without both flags |
| `--rule NAME` | read `S3_BACKUP_RULES` YAML (`prefix`, `source`), expand placeholders with UTC now; explicit args override rule values |

Always report results as JSON like the plugin, and redact access/secret keys from any error text.

## Setup
1. Create a bucket and an access key pair at the provider.
2. `export S3_BACKUP_BUCKET=... S3_BACKUP_REGION=... S3_BACKUP_ACCESS_KEY=... S3_BACKUP_SECRET_KEY=...` and, for R2/MinIO, `S3_BACKUP_ENDPOINT=https://...`. Keep them in a 0600 env file, never in rule files or command arguments.
3. `pip install boto3 pyyaml` (PyYAML only if using rules files).
4. Optional: write `~/.hermes/s3-backup.rules.yaml` (or point `S3_BACKUP_RULES` elsewhere) with named rules.

## Limits
- `hermes s3` CLI command and native tool registration are Hermes-specific; Claude runs the equivalent Python or aws commands.
- Credentials and uploaded data go to the chosen third-party object store; uploads may incur storage and transfer charges.
- Deletion is irreversible; the plugin's `confirm` and `recursive` guards must be honoured by asking the user explicitly.
- Multipart or resumable uploads, retries and checksums beyond boto3 defaults are not implemented in the plugin and not promised here.
- Upstream `skills/s3/SKILL.md` is copied to `references/upstream-s3.md` (MIT).

## Source
- Catalog entry (reviewed commit): https://github.com/lagoon-labs/hermes-s3-plugin/tree/3d1514e270914d89b4e99db9917eaec25d4e6688
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/s3.yaml
