---
name: daily-reflection-publisher
description: Turn mixed-language personal daily logs, journals, chat fragments, reminders, and informal "流水账" notes into a complete Markdown reflection summary for personal growth and knowledge storage, then optionally publish the confirmed entry to the user's configured GitHub repository. Use when the user says phrases like "生成一下今天流水账", "总结今天流水账", "做一下今日复盘", asks to summarize today's personal record, create an入库 Markdown,整理个人流水账, choose an output language, analyze emotional state/work/interpersonal relationships, extract facts/thoughts/preferences/highlights/problems/actions, or convert raw life notes into a coherent daily archive.
---

# Daily Reflection Publisher

## Purpose

Create a complete daily Markdown reflection from messy personal notes. Preserve concrete facts, then extract useful thinking, growth signals, exposed problems, stable patterns, and actions without turning every passing mood, one-off event, or uncertain inference into a permanent rule.

## Workflow

1. Identify the target date. If the user does not specify a date, use the current date from the environment.
2. Confirm the output language before generating the reflection if the user has not already specified it. Offer concise choices:
   - Preserve mixed language: keep each item close to the source language.
   - Chinese: produce section headings and summaries in Chinese while preserving names, quotes, and technical terms.
   - English: produce section headings and summaries in English while preserving names, quotes, and technical terms.
   - Custom: follow the user's requested language or bilingual style.
3. Show the raw record first. Present the source notes under a short raw-record heading in the selected output language. Lightly normalize obvious formatting only; do not rewrite the evidence at this stage.
4. Read the source notes as raw evidence. Accept mixed formats: prose, bullets, chat logs, task lists, screenshots transcribed by the user, or pasted fragments.
5. Group entries by topic before summarizing. Common topics include work, projects, relationships, health, money, learning, travel, tools, household, decisions, and emotions.
6. Separate evidence, reflection, and durable information:
   - Facts: concrete events, actions, decisions, commitments, constraints, and outcomes.
   - Thoughts: questions, realizations, delayed interpretations, decision logic, and ideas worth revisiting.
   - Long-term preferences: stable patterns, recurring dislikes, workflow preferences, communication preferences, values, or operating principles.
   - Highlights: meaningful progress, useful discoveries, positive moments, or important signals.
   - Exposed problems: blockers, misjudgments, repeated friction, emotional triggers, unhealthy defaults, or missing information.
   - Actions: follow-ups, checks, experiments, commitments, and concrete next steps.
   - Noise: repeated filler, low-signal complaints, duplicates, raw timestamps, temporary moods without action, and details that should not be stored.
7. Mark uncertainty explicitly. Use the selected output language for uncertainty labels, such as "待确认" in Chinese or "To verify" in English.
8. Filter noise internally. Do not show a noise section unless the user explicitly asks to see what was omitted.
9. Produce one coherent Markdown document with a personal-growth orientation and the selected output language. Do not output a fragmented extraction unless the user asks for raw tables.
10. Ask the user to confirm whether anything needs to be modified. Do not publish or push anything before explicit confirmation.
11. If the user says no changes are needed or explicitly approves publishing, save the confirmed Markdown entry to a temporary Markdown file, then run `scripts/publish_daily_reflection.py` to commit and push it to the user's configured GitHub repository. Follow `references/github-publish-workflow.md`.
12. After a successful publish, delete the temporary Markdown input file. Keep it only if publishing fails, so the user can inspect or retry from that local file.

## Direct Invocation

When the user says "生成一下今天流水账", "总结今天流水账", "做一下今日复盘", or a similar short request, produce the daily Markdown reflection for the current date using available conversation context and any notes the user provides in the same turn. Do not ask the user to choose a structure; use the default output structure. If the output language is unspecified, ask only for the language choice before generating.

If there are no source notes in the current context, still create the skeleton and mark sections as "信息不足", then invite the user to paste the raw流水账 only if needed.

After generating the reflection, always ask: "是否有需要修改的地方？如果没有，我可以把这篇流水账提交到你配置的 GitHub 仓库。" Wait for the user's answer.

## Default Output Structure

Use this structure unless the user asks for a different one. Translate section headings into the selected output language. For preserve-mixed mode, use the user's dominant language for headings.

```markdown
# YYYY-MM-DD 个人复盘总结

## 原始记录
> Include the raw notes or a concise evidence-preserving normalization of them. If the source is very long, summarize the raw record by topic and say it is a condensed raw record.

## 今日概览
- 2-5 bullets summarizing the day as a whole, including the most important growth signal if present.

## 事实记录
### 工作 / 项目
- Concrete facts, decisions, actions, blockers, and results.

### 关系 / 沟通
- Concrete interactions, communication moments, misunderstandings, emotional signals, and relationship context.

### 生活 / 健康 / 金钱
- Concrete personal events, health, errands, purchases, logistics, money, investing, and household context.

### 工具 / 系统 / 信息源
- Tools used, setup changes, useful sources, or technical context worth remembering.

## 今日思考
- Questions, realizations, delayed interpretations, decision logic, and ideas worth revisiting.
- Include "我后来意识到..." style reflections when the notes contain delayed understanding.

## 状态分析
### 情绪状态
- Overall emotional tone, energy level, stressors, positive signals, delayed emotional processing, and uncertainty. Ground claims in the source notes.

### 工作情况
- Workload, progress, blockers, feedback, collaboration state, delivery risk, and capability growth.

### 人际交往与关系
- Important interactions, relationship signals, communication dynamics, misunderstandings, care, support, or boundaries.

## 暴露的问题
- Blockers, friction, judgment gaps, emotional triggers, workflow instability, sleep/health issues, or missing information.
- Keep this practical and non-judgmental.

## 长期偏好与稳定模式
- 已确认偏好: preferences supported by repeated evidence or strong explicit wording.
- 待确认模式: weak patterns or inferred preferences that need more evidence.
- 一次性事件: items that should not be promoted to a stable preference.

## 发现的亮点
- Progress, insights, good decisions, useful discoveries, or moments worth preserving.

## 可转化的行动
- Commitments, follow-ups, checks, experiments, habit/system adjustments, and research tasks.

## 可入库摘要
- A concise final version suitable for direct storage in a personal Markdown knowledge base.
```

## Summarization Rules

- Preserve specific names, project names, file paths, dates, amounts, and decisions when they matter.
- Support multilingual inputs and outputs. Follow the user's selected output language.
- In preserve-mixed mode, preserve the source language locally: Chinese notes remain Chinese, English notes remain English, and mixed notes can stay mixed.
- In Chinese or English mode, translate summaries and section headings into the selected language, but preserve names, quotes, tool names, task names, URLs, code identifiers, and technical terms when translation would reduce precision.
- Rewrite messy notes into clear prose, but do not invent missing causes or motivations.
- Prefer compact bullets over long paragraphs.
- Keep the tone factual, reflective, and practical. Avoid therapy-style interpretation unless the user explicitly asks for it.
- Do not over-extract permanent preferences from a single isolated event.
- For personal growth, prioritize reusable lessons, decision patterns, and next actions over exhaustive chronology.
- Treat exported AI logs and timestamped chat lists as supporting evidence. Summarize the meaning of the events instead of copying the full timeline unless exact timing matters.
- Omit noise from the visible output by default. Use noise filtering to decide what not to include, but do not display a separate omitted-noise list unless asked.
- In "状态分析", distinguish observed evidence from interpretation. Use cautious wording such as "看起来", "可能", or "待确认" when inferring emotion or relationship meaning.
- Keep "暴露的问题" useful and concrete; do not turn normal fatigue, one-off delay, or casual emotion into a character judgment.
- If the source contains sensitive information, summarize at the useful abstraction level and avoid copying secrets, credentials, tokens, or unnecessarily private raw content.
- If the user asks for "入库", make the final section clean enough to paste into a memory system or Markdown knowledge base.

## Handling Sparse or Noisy Input

If the input is too short or ambiguous, still produce a useful summary, but add a short "信息不足" note under relevant sections. Do not ask for clarification unless a missing date, target scope, or privacy boundary would materially change the output.

## Reference

For the canonical Markdown skeleton and section intent, see `references/daily-summary-template.md`.

For the confirmed-entry GitHub publishing workflow, see `references/github-publish-workflow.md`.

For deterministic publishing after user approval, use `scripts/publish_daily_reflection.py`.
