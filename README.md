# Daily Reflection Publisher

Daily Reflection Publisher is a Codex skill for turning messy daily notes into a structured Markdown reflection, then publishing the confirmed entry to a GitHub repository.

It is designed for personal growth logs, daily retrospectives, and lightweight knowledge-base storage.

## What It Does

- Shows the raw daily record before summarizing.
- Generates a Markdown daily reflection with facts, thoughts, emotional state, work state, relationship signals, exposed problems, highlights, actions, and an archive-ready summary.
- Keeps Chinese, English, and mixed-language notes in their natural language.
- Asks for confirmation before publishing.
- Publishes the confirmed Markdown entry to a GitHub repository using `scripts/publish_daily_reflection.py`.

## Install

Copy this folder into your Codex skills directory:

```bash
mkdir -p ~/.codex/skills
cp -R daily-reflection-publisher ~/.codex/skills/
```

Then invoke it in Codex:

```text
Use $daily-reflection-publisher to generate today's daily reflection:

[paste your raw daily notes here]
```

Chinese trigger examples also work:

```text
用 $daily-reflection-publisher 生成一下今天流水账：

[粘贴今天的原始记录]
```

```text
做一下今日复盘：

[粘贴今天的原始记录]
```

## Configure GitHub Publishing

This repository does not include a hardcoded GitHub account or target repo. You must use your own GitHub repository for publishing.

Create an empty repository, for example:

```text
https://github.com/YOUR_USERNAME/YOUR_DAILY_REPO.git
```

When publishing manually, pass your repo URL:

```bash
scripts/publish_daily_reflection.py \
  --date 2026-05-15 \
  --input /path/to/confirmed-entry.md \
  --repo-url https://github.com/YOUR_USERNAME/YOUR_DAILY_REPO.git
```

Or configure it with an environment variable:

```bash
export DAILY_REFLECTION_REPO_URL="https://github.com/YOUR_USERNAME/YOUR_DAILY_REPO.git"
```

Optional local clone directory:

```bash
export DAILY_REFLECTION_REPO_DIR="$HOME/.daily-reflection-publisher/repo"
```

If no existing date-based convention is found in the target repo, the script writes entries to:

```text
daily/YYYY-MM-DD.md
```

## Publishing Flow

The skill should publish only after you approve the generated reflection.

1. Generate the Markdown reflection.
2. Review the output.
3. Confirm that no changes are needed.
4. Run the publish script with your configured GitHub repo.
5. Delete the temporary input Markdown after a successful publish.

The script refuses to overwrite an existing date file unless `--overwrite` is passed. Use that option only after explicitly deciding to replace the existing entry.

## Script Options

```bash
scripts/publish_daily_reflection.py --help
```

Common options:

- `--repo-url`: target GitHub repository URL.
- `--repo-dir`: local clone directory.
- `--output-path`: repo-relative path for the entry.
- `--dry-run`: show what would happen without writing, committing, or pushing.
- `--overwrite`: allow replacing an existing entry.
- `--no-push`: commit locally but skip push.

## Privacy Notes

Daily reflections can contain sensitive personal information. Before making your target repository public, review the generated Markdown carefully. For private journals, use a private GitHub repository.
