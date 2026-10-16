# Repository instructions

This repository publishes Deep Research, an English Jekyll site hosted at
https://grjus.github.io/. Read this file before editing or publishing a briefing.

## Where instructions and content live

- `docs/automation-prompt.md`: the scheduled agent's research task and editorial rules.
- `docs/examples/briefing.md`: a complete, fictional example of the required format.
- `docs/examples/README.md`: filename, description, reduced-report, and generated-post examples.
- `reports/YYYY-MM-DD_HHMM_deepresearch.md`: the plain Markdown report and downloadable original.
- `_posts/YYYY-MM-DD-HHMM-deepresearch.md`: the generated Jekyll post.
- `scripts/import_report.py`: validation and import. Use it rather than writing post front matter by hand.

Paths in this guide are relative to the repository root. Do not assume a particular
user's home directory. Python 3.9+, Ruby 3.3/Bundler, Git, authenticated GitHub CLI
(`gh`), and network access are prerequisites. Install the build dependencies with
`bundle install` before enabling unattended publication. The runner needs permission
to push a briefing branch to `grjus/grjus.github.io`, open pull requests, and read PR checks. Do not change account
permissions, branch protections, or GitHub Pages settings to work around a failure.

If the publication agent itself runs inside GitHub Actions, its PR-creation credential
affects whether checks run unattended. PRs created with that workflow's default
`GITHUB_TOKEN` can require approval before checks start. Configure a GitHub App token
or personal access token when unattended triggering is required; do not change
credentials during a briefing run. See [GitHub's workflow-trigger documentation](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow#triggering-a-workflow-from-a-workflow).

## Briefing contract

1. Capture one run time in `Europe/Warsaw`. The filename uses that time to the minute.
   Compute the window as exactly 72 elapsed hours, using UTC arithmetic, then display
   both endpoints with Warsaw's actual offsets. The window end must match the filename.
2. Use a findings-led `#` headline, with no date/time or generic “Deep Research” prefix.
   The headline becomes the post title. `--description` is a separate, concise archive
   preview; it is not the title.
3. Use `## Executive Summary` first, with 1–5 sourced bullets. Follow it with qualifying
   sections in this order: `## AI/ML Articles`, `## Azure/AWS Articles`,
   `## AI/ML Repositories`. Omit sections with no findings.
4. Maximum counts are 5 articles, 2 cloud updates, and 2 repositories. They are not
   targets. Number real items from 1 within each section using `### 1. Title`.
   Never add placeholder items or empty sections. If nothing qualifies, do not publish.
5. Articles and cloud updates use these metadata bullets, in order:
   `Source`, `Date`, `Tags`, `Link`. Repositories use `Stars`, `Language`, `License`,
   `Last commit`, `Link`. See the example for exact Markdown syntax.
6. Every item has exactly `**Summary**`, a blank line, and 1–8 flat bullet points.
   Prefer 4–6. Include evidence, a practical takeaway, and a relevant limitation.
   Do not use TLDR, a Description paragraph, nested summary lists, or extra headings.
7. Keep publication evidence within the run window. Use primary sources and link all
   material claims. Deduplicate underlying stories across sections. Never copy fictional
   example claims, example URLs, or example metadata into a real briefing.

## Pull request workflow for scheduled runs

These steps apply when the agent is invoked to execute `docs/automation-prompt.md`
and prepare a briefing for review. That task authorizes committing the new report/post
pair to a dedicated branch, pushing that branch, and opening a pull request against
`main` without requesting confirmation for each run. Never push briefing commits
directly to `main`, merge a PR, or enable automatic merging. A reviewer controls merging;
GitHub Pages publishes after merge. Stop the scheduled task at the PR handoff.
A request to edit these instructions alone does not authorize opening a PR.
The job is intended to run every three days, researching the previous 72 elapsed hours.
Do not create a schedule from this file; the scheduler is configured separately.

### 1. Check the checkout and create a briefing branch

Run from the repository root:

```sh
git remote get-url origin
git status --porcelain
gh auth status
git fetch origin main
```

Confirm `origin` identifies `grjus/grjus.github.io`. Require a clean working tree.
If unrelated changes exist, stop and report them; do not stash, reset, delete,
commit, or submit someone else's work. Stop on authentication or permission failures.

Capture the run time and name its branch `codex/briefing-YYYY-MM-DD-HHMM` using
Europe/Warsaw. Before creating a branch or report, check for a previous attempt:

```sh
gh pr list --repo grjus/grjus.github.io --state all --head codex/briefing-2026-10-16-1330 --json number,url,state,headRefName,baseRefName
```

The commands use an illustrative run time; substitute this run's actual value.
If an open PR already exists, inspect it and reuse its branch and PR for the same run.
If it is merged, report the existing PR and do not create another. If it was closed
without merging, report that state rather than reopening it or creating a duplicate.
If a local or remote branch exists without a PR, inspect and resume that attempt;
do not reset or overwrite it. Preserve the original run time on retries.

For a new run, create a branch directly from the fetched `origin/main`:

```sh
git switch -c codex/briefing-2026-10-16-1330 origin/main
git rev-parse HEAD
git rev-parse origin/main
```

The two commit IDs must match at the start of a new run. Do not carry unrelated local
commits into a briefing PR. Do not force push or modify branch protections.

### 2. Research, write, and validate

Follow `docs/automation-prompt.md`, comparing candidate stories with recent reports
to avoid re-publishing unchanged material. Keep the captured run time on retries.
Write one report under `reports/`. Read the complete file back before importing.

Example commands below illustrate a run at 13:30 on October 16, 2026. Substitute
the actual run's filename and factual description; do not publish these literals:

```sh
python3 scripts/import_report.py reports/2026-10-16_1330_deepresearch.md --check
python3 scripts/import_report.py reports/2026-10-16_1330_deepresearch.md --description 'New evidence on agent oversight and policy enforcement.'
python3 -m unittest discover -s tests
python3 -m scripts.validate_archive
bundle exec jekyll build --strict_front_matter
git diff --check
```

`--check` validates without writing. The importer creates the post and keeps the
downloadable report in sync. It refuses to overwrite different content. A matching
report/post pair can be imported again without changes. Resolve collisions by
inspecting the existing files; do not invent another run time to bypass protection.

Inspect `_site/index.html` and the new post's rendered HTML. Verify the title,
description, source links, ordered sections, Summary bullets, and Markdown download.
The expected post URL after this PR is merged and deployed is
`https://grjus.github.io/2026/10/16/1330-deepresearch/`.
Verify that the build generated that path. Do not open the source `index.html` as a
browser preview; serve `_site/` over HTTP instead. Never commit `_site/`.

The validator checks structure and timing, not source truth, publication eligibility,
or whether a claim accurately describes the evidence. The research agent must check
those separately. A successful build does not prove that a briefing is accurate.

### 3. Commit and push only the briefing branch

Review the status and stage only the pair for this run:

```sh
git branch --show-current
git status --short
git add -- reports/2026-10-16_1330_deepresearch.md _posts/2026-10-16-1330-deepresearch.md
git diff --cached --check
git diff --cached --stat
git diff --cached
git commit -m "Add briefing for 2026-10-16 13:30 Europe/Warsaw"
git push --set-upstream origin HEAD:refs/heads/codex/briefing-2026-10-16-1330
git rev-parse HEAD
```

Before committing or pushing, confirm that the current branch is this run's
`codex/briefing-...` branch and exactly the report/post pair is staged. No unrelated
files may change during the run. Never use `git add .` or `git commit -a` for this task.
Inspect `git diff --stat origin/main...HEAD` to ensure the entire PR contains only the
intended pair. A retry that already has the correct commit needs no additional commit.
If another process changed this branch, stop and report the conflict; do not force push.

### 4. Open and verify the pull request

Open one regular PR against `main` after local validation passes. Include the run
window, item counts, a short description of the findings, and the checks performed.
Use a temporary body file so Markdown and newlines are preserved. For example:

```sh
briefing_pr_body=$(mktemp)
cat > "$briefing_pr_body" <<'EOF'
## Briefing

Independent checks strengthen agent oversight.

- Window: 2026-10-13 13:30 +02:00 to 2026-10-16 13:30 +02:00 (Europe/Warsaw)
- Findings: 1 AI/ML article, 1 cloud update, 1 repository
- Expected post path after merge: /2026/10/16/1330-deepresearch/

## Validation

- Source claims and publication dates checked against primary evidence.
- Importer validation and unit tests passed.
- Jekyll build and rendered content checked.
- Plain report and generated post reviewed together.
EOF
gh pr create --repo grjus/grjus.github.io --base main --head codex/briefing-2026-10-16-1330 --title "Briefing: Independent checks strengthen agent oversight" --body-file "$briefing_pr_body"
rm -- "$briefing_pr_body"
```

Replace the example title, window, counts, paths, and check results with actual facts.
Never include a check as passed unless it was performed successfully. Before retrying
PR creation, run the PR lookup from step 1 again; creation may have succeeded even if
its response was interrupted. Update the existing open PR instead of creating another.

Verify the actual PR number returned by GitHub:

```sh
gh pr view PR_NUMBER --repo grjus/grjus.github.io --json url,state,baseRefName,headRefName,headRefOid,files
gh pr checks PR_NUMBER --repo grjus/grjus.github.io
```

The `Validate briefings` GitHub Actions workflow runs on PRs targeting `main`,
including new commits to an open PR. Its `Briefing validation` job runs the unit
tests, validates every report/post pair, and builds Jekyll. Read these results
before handing off the PR. The workflow validates content and builds the site;
it does not publish or merge. Report pending or failing checks accurately.

Require an open PR with base `main`, this run's branch and commit SHA as its head,
and only the intended two files. Read available check results. If no checks are
configured, say so; local validation is still required. If checks are pending or
failing, report their status accurately and leave the PR open for review. Do not
wait for a merge, merge it yourself, or enable automatic merging.

Return the title, selected-item counts, run window, branch, commit SHA, PR URL, and
local/PR check results. The outcome is “PR opened for review,” not “published.” Do
not require the prospective public post URL to exist: deployment occurs only after
a reviewer merges the PR. Pages deployment verification is a separate post-merge task.

If no items qualify, create no commit or PR; report that in the scheduler's run
result only. If any step fails, preserve verified work and identify the failed step.
Distinguish a local draft, a pushed branch, and a confirmed open PR. Do not claim a
failed or pending step succeeded. Do not send emails, chat messages, or other external
notifications unless the scheduler's user instructions explicitly authorize them.
