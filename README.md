# Repo Intelligence Hub

Repo Intelligence Hub is a repository-centered catalog for **SpiralCloudOmega**. It turns a large GitHub footprint into a searchable inventory, ranked connector shortlist, and agent handoff workspace for future analysis.

## Current snapshot

- Total indexed repos: **804**
- Original repos: **18**
- Forks: **786**
- High-priority repos (P4-P5): **4**
- Priority 3 repos needing review: **7**
- Low-signal repos (P1-P2): **793**

## What this hub contains

- A normalized inventory in JSON and CSV formats.
- Split collections for originals, forks, stale/archive candidates, and high-priority repos.
- Indexes by priority, topic, language, and classification cluster.
- Connector guidance for choosing the best repositories to expose to ChatGPT or other repo-aware agents.
- Summary stubs and agent handoff batches for ongoing manual enrichment.

## Key files

- `repos/inventory.json` — master normalized repo inventory.
- `repos/inventory.csv` — spreadsheet-friendly inventory export.
- `repos/originals.json` — non-fork repositories.
- `repos/forks.json` — forked repositories.
- `repos/high-priority.json` — P4/P5 repositories.
- `indexes/priority-ranking.json` — ranked inventory sorted by priority and recency.
- `indexes/topic-map.json` — topic to repository lookup.
- `indexes/language-map.json` — language to repository lookup.
- `indexes/repo-clusters.json` — category-based clusters.
- `indexes/recommended-chatgpt-connector-selection.md` — top connector recommendations.
- `agent-handoff/` — manual review instructions, batches, and completion tracking.

## Directory structure

```text
repos/
  inventory.json
  inventory.csv
  originals.json
  forks.json
  archived-or-stale.json
  high-priority.json
  raw-search-output.json
indexes/
  priority-ranking.json
  topic-map.json
  language-map.json
  repo-clusters.json
  recommended-chatgpt-connector-selection.md
summaries/
  README.md
  *.md summary stubs for high-priority repos
agent-handoff/
  instructions.md
  batch-template.md
  batch-001.md
  batch-002.md
  completion-log.md
scripts/
  collect-repos-gh.sh
  normalize-inventory.py
  generate-summary-stubs.py
```

## Priority model

The inventory uses a 1-5 scale:

- **5** — very important original repo; active AI, automation, infrastructure, devtools, app, or API work.
- **4** — strong candidate with meaningful code or documentation.
- **3** — plausible value, but needs manual review.
- **2** — lower-signal, often stale, minor, duplicate, or fork/reference-heavy.
- **1** — empty, archived, generated, or otherwise safe to skip by default.

## Classification model

Primary categories include:

- `ai-ml`
- `automation`
- `infrastructure`
- `devtools`
- `web-app`
- `api-backend`
- `frontend`
- `data`
- `docs`
- `experiment`
- `fork-reference`
- `empty-low-signal`
- `unknown`

## Highest-priority repos right now

- **SpiralCloudOmega/DevTeam6** — P5 — High-signal original repository with active engineering value for AI, automation, infrastructure, or developer tooling review.
- **SpiralCloudOmega/PACKTPub_The_Digital_Library_Of_Alexandria** — P4 — Strong candidate for detailed review because it appears to contain meaningful code, docs, or reusable implementation patterns.
- **SpiralCloudOmega/react-postgres-fullstack-template** — P4 — Strong candidate for detailed review because it appears to contain meaningful code, docs, or reusable implementation patterns.
- **SpiralCloudOmega/gemini-mentor** — P4 — Strong candidate for detailed review because it appears to contain meaningful code, docs, or reusable implementation patterns.
- **SpiralCloudOmega/revithion-studio** — P3 — Potentially useful after manual review to confirm scope, quality, and relationship to adjacent repositories.
- **SpiralCloudOmega/revithion** — P3 — Potentially useful after manual review to confirm scope, quality, and relationship to adjacent repositories.
- **SpiralCloudOmega/astro-blog-starter-template1** — P3 — Potentially useful after manual review to confirm scope, quality, and relationship to adjacent repositories.
- **SpiralCloudOmega/revithionstudio** — P3 — Potentially useful after manual review to confirm scope, quality, and relationship to adjacent repositories.
- **SpiralCloudOmega/astro-blog-starter-template** — P3 — Potentially useful after manual review to confirm scope, quality, and relationship to adjacent repositories.
- **SpiralCloudOmega/workers-for-platforms-template** — P3 — Potentially useful after manual review to confirm scope, quality, and relationship to adjacent repositories.

## Cluster counts

- `ai-ml`: 212
- `automation`: 20
- `infrastructure`: 11
- `devtools`: 130
- `web-app`: 48
- `api-backend`: 46
- `frontend`: 21
- `docs`: 146
- `fork-reference`: 786


## How to refresh the hub

### Option 1: Refresh from GitHub CLI

If `gh` is authenticated:

```bash
./scripts/collect-repos-gh.sh
python scripts/normalize-inventory.py --input repos/raw-gh-output.json
python scripts/generate-summary-stubs.py
```

### Option 2: Refresh from saved GitHub Search API payloads

Merge one or more saved search JSON payloads and then normalize:

```bash
python scripts/normalize-inventory.py --input repos/raw-search-output.json
python scripts/generate-summary-stubs.py
```

## Recommended workflow

1. Start with `indexes/recommended-chatgpt-connector-selection.md`.
2. Review `repos/high-priority.json` and the summary stubs in `summaries/`.
3. Use `agent-handoff/batch-001.md` and `agent-handoff/batch-002.md` for deeper manual passes.
4. Re-run normalization after any refreshed raw data pull.

## Notes

- The current inventory snapshot was built from merged GitHub search result payloads and deduplicated by `nameWithOwner`.
- The snapshot currently covers **all 804 discovered repositories** in the available source data.
