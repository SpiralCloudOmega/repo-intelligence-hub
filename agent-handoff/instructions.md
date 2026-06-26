# Agent Handoff Instructions

Use this folder to coordinate deeper manual review after the repository inventory has been refreshed.

## Workflow
1. Read `agent-handoff/completion-log.md` to see what is already covered.
2. Pick the next open batch file.
3. For each repo in the batch, inspect the repository directly on GitHub.
4. Update the relevant summary stub in `summaries/`.
5. If the repo deserves reprioritization, update `repos/inventory.json` by rerunning `scripts/normalize-inventory.py` against refreshed raw data.
6. Mark progress in `completion-log.md`.

## Review expectations
- Confirm repo purpose and maturity.
- Capture architecture, automation, and integration relevance.
- Note whether the repo belongs in the connector short list.
- Flag archival, emptiness, or duplication quickly.
