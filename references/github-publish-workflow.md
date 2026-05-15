# GitHub Publish Workflow

Use this only after the user explicitly confirms the generated daily reflection is final.

The script is the source of truth for publishing:

```bash
scripts/publish_daily_reflection.py \
  --date YYYY-MM-DD \
  --input /path/to/confirmed-entry.md \
  --repo-url https://github.com/YOUR_USERNAME/YOUR_REPO.git
```

User configuration:

- The user must provide their own GitHub repository URL with `--repo-url`, or set `DAILY_REFLECTION_REPO_URL`.
- Optional local clone path can be set with `--repo-dir`, or `DAILY_REFLECTION_REPO_DIR`.
- Default local clone path: `~/.daily-reflection-publisher/repo`
- Fallback path when no repo convention is found: `daily/YYYY-MM-DD.md`

Rules:

- Do not run the script before explicit user approval.
- Do not overwrite an existing date file unless the user approves `--overwrite`.
- Use `--dry-run` when checking the target path before publishing.
- Delete the temporary Markdown input file after a successful publish.
- Keep the temporary input file only when publish fails, and report its path for retry or inspection.
- If the script fails because of authentication, remote access, branch protection, or unrelated local changes, stop and report the exact error plus the local input file path.
