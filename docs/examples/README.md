# Briefing examples

`briefing.md` is a fictional format fixture, not publishable research. All domains,
results, repositories, and metadata in it are illustrative. It lives under `docs/`
so Jekyll excludes it. Never copy it into `reports/` as a real publication.

## Filename, title, and description

For a run at `2026-10-16 13:30 +02:00` in Europe/Warsaw:

- Report: `reports/2026-10-16_1330_deepresearch.md`
- First line: `# Independent checks strengthen agent oversight`
- Description: `Research on independent verification, plus cloud controls and an agent evaluation tool.`
- Generated post: `_posts/2026-10-16-1330-deepresearch.md`
- Public path: `/2026/10/16/1330-deepresearch/`

The filename carries the run time. The first heading carries the editorial title.
The description is a separate archive preview. The importer generates front matter
like this; the research agent does not write it into the plain report:

```yaml
---
title: "Independent checks strengthen agent oversight"
date: "2026-10-16 13:30:00 +0200"
description: "Research on independent verification, plus cloud controls and an agent evaluation tool."
category: "Research briefing"
report_file: "2026-10-16_1330_deepresearch.md"
---
```

The post body starts with the window line, followed by the Executive Summary.
The layout renders the title, so the post body must not repeat its `#` heading.

## A run with fewer findings

The complete example contains one entry in each section. That is valid even though
the maximums are 5, 2, and 2. If only the AI/ML article qualifies, retain the title,
window, Executive Summary, and AI/ML Articles section. Remove the cloud and repository
sections entirely, and remove their takeaways from the Executive Summary. Do not
replace them with text about missing findings.

If two AI/ML articles qualify, use `### 1. ...` and `### 2. ...`; start numbering
again at 1 in the next section. Each item gets its own metadata and Summary list.

If no findings qualify, create no report or post. Record the outcome in the run result.

## Examples to reject

- A heading such as `# Deep Research: 2026-10-16 13:30`: repeats the publication metadata.
- An empty section or a placeholder item such as `### 2. Nothing notable.`: counts are maximums.
- A `**TLDR:**` paragraph: use exactly `**Summary**` followed by 1–8 flat bullets.
- Nine Summary bullets, missing metadata, or a bare URL in the Link field.
- A 24-hour window, a filename/window mismatch, or an old story with a fresh crawler date.
- A repo push time reported as its last default-branch commit date.
- A fictional example treated as evidence, or an invented number used to fill a section.
