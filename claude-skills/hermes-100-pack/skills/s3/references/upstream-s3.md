<!-- Copied from https://github.com/lagoon-labs/hermes-s3-plugin @ 3d1514e270914d89b4e99db9917eaec25d4e6688, MIT. Original authors retain copyright. -->
# S3 backup

Use the `s3-push`, `s3-pull`, `s3-ls`, and `s3-rm` tools, or the equivalent `hermes s3 push`, `pull`, `ls`,
and `rm` commands.

Set `S3_BACKUP_ENDPOINT`, `S3_BACKUP_REGION`, and `S3_BACKUP_BUCKET`, plus
`S3_BACKUP_ACCESS_KEY` and `S3_BACKUP_SECRET_KEY`. Keep credentials in the
process environment or `~/.hermes/.env`; never put them in rules, tool
arguments, or repository files. `S3_BACKUP_RULES` optionally points to YAML
and defaults to `~/.hermes/s3-backup.rules.yaml`.

Example rule:

```yaml
project-build:
  prefix: backups/project/{date}
  source: ~/my-project
```

Use `--rule project-build` to supply omitted values. Explicit `--src`/`--dst`
values override the rule. Supported placeholders are `{date}`, `{ts}`,
`{year}`, `{month}`, and `{day}`. Existing objects are skipped unless push
uses `--force`. Pull rejects absolute, parent-directory, and symlink-escaping
object paths. Deletion always needs `--confirm`; deleting a prefix also needs
`--recursive`.
