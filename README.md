# Deep Research

A static Jekyll publication for briefings every three days on AI agents, research, and Azure/AWS infrastructure. Public site: [grjus.github.io](https://grjus.github.io/).

## Scheduled briefing pull requests

The repository provides two agent instruction files:

- [Research task prompt](docs/automation-prompt.md): what to research, how to select findings, and the exact briefing structure.
- [Repository instructions](AGENTS.md): prerequisites, validation, import, branch creation, pull requests, check results, and failure handling.

Configure a separate scheduled agent to run in this repository with this task:

> Read AGENTS.md, then execute docs/automation-prompt.md to research a three-day briefing and open a pull request against main. Follow its examples. Push only the dedicated briefing branch; do not push to main, merge, or enable automatic merging.

The runner needs Python 3.9+, Ruby/Bundler with `bundle install` completed, Git, authenticated GitHub CLI, web research access, permission to push briefing branches, create PRs, and read PR checks. It must start from a clean checkout and create its briefing branch from the fetched `origin/main`. The job should run every three days and cover the previous 72 elapsed hours. This setup prepares the repository; it does not create a schedule or grant account permissions.

## Briefing convention

See the [complete fictional briefing](docs/examples/briefing.md) and [filename, metadata, and reduced-report examples](docs/examples/README.md). Examples live under `docs/` and are excluded from the site. The archive starts empty; no historical briefing is retained.

- English, neutral, sourced content from the previous 72 elapsed hours.
- A findings-led title; date/time belongs in the filename, post metadata, and research window.
- Executive Summary, then up to 5 AI/ML articles, 2 cloud updates, and 2 repositories in that order.
- Omit empty sections and unused slots. Skip publication when no findings qualify.
- Each item has exact metadata fields and **Summary** followed by 1–8 flat bullets.

Save plain Markdown in `reports/YYYY-MM-DD_HHMM_deepresearch.md`, then run:

```sh
python3 scripts/import_report.py reports/YYYY-MM-DD_HHMM_deepresearch.md --check
python3 scripts/import_report.py reports/YYYY-MM-DD_HHMM_deepresearch.md --description 'A factual archive preview.'
python3 -m unittest discover -s tests
python3 -m scripts.validate_archive
bundle exec jekyll build --strict_front_matter
```

The first Markdown heading supplies the title. `--description` supplies the separate preview below the title. The importer generates `_posts/YYYY-MM-DD-HHMM-deepresearch.md`; submit it together with the report in the same PR. A report in `reports/` alone does not appear in the archive. Importing the same pair again makes no content changes; different existing content is protected from overwrite.

## Preview and hosting

Use Ruby 3.3, matching `.ruby-version` and the CI build. macOS's bundled Ruby 2.6
cannot install the current dependencies. If using Homebrew, install and select Ruby
before running Bundler:

```sh
brew install ruby@3.3
export PATH="$(brew --prefix ruby@3.3)/bin:$PATH"
ruby -v
bundle install
bundle exec jekyll serve
```

`ruby -v` should report 3.3.x. The PATH change applies to the current terminal;
add that export line to your shell configuration to keep using it in new terminals.

PRs targeting `main` run the [Validate briefings workflow](.github/workflows/validate-briefings.yml). It runs unit tests, validates report structure and generated-post consistency, and builds Jekyll. It also supports manual runs. The workflow has read-only repository permissions and does not deploy or merge. To prevent merging on failure, a repository administrator must make `Briefing validation` a required check in the branch rules; adding the workflow alone does not enforce that restriction.

Jekyll generates the finished site in `_site/`. Use `bundle exec jekyll serve` for a local preview, normally at `http://127.0.0.1:4000/`. Opening the source `index.html` directly shows unprocessed template code.

The archive shows 10 briefings per page, newest first, with Previous/Next links when needed. Dark mode follows the system preference until a reader saves a choice with the header toggle.

GitHub Pages builds from the repository root on `main`. Do not add `.nojekyll` or commit `_site/`. Follow `AGENTS.md` to open the briefing PR. A reviewer merges it; GitHub Pages deploys afterward. The scheduled agent stops at the PR handoff. `docs/`, `scripts/`, `tests/`, and `AGENTS.md` are excluded from the public site.
