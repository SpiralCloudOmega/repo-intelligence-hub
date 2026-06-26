#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path


def slugify(name):
    return re.sub(r"[^a-zA-Z0-9]+", "-", name).strip("-").lower()


def main():
    parser = argparse.ArgumentParser(description="Generate summary stubs for high-priority repositories.")
    parser.add_argument("--inventory", default="repos/high-priority.json")
    parser.add_argument("--output-dir", default="summaries")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    repos = json.loads(Path(args.inventory).read_text())
    created = []
    current_files = set()
    for repo in repos:
        slug = slugify(repo["nameWithOwner"])
        path = output_dir / f"{slug}.md"
        current_files.add(path.name)
        if not path.exists():
            created.append(path.name)
        content = f"""# {repo['nameWithOwner']}

- URL: {repo['url']}
- Priority: {repo['priority']}
- Status: {repo['status']}
- Language: {repo['primaryLanguage'] or 'unknown'}
- Classification: {', '.join(repo['classification'])}
- Last Updated: {repo['lastUpdated'] or 'unknown'}

## Current Understanding
{repo['description'] or 'No description captured yet.'}

## Why It Matters
{repo['whyUseful']}

## Suggested Next Action
{repo['recommendedNextAction']}

## Review Checklist
- [ ] Confirm project purpose from README and top-level files
- [ ] Capture core modules, workflows, or APIs
- [ ] Note dependencies, deployment/runtime expectations, and automation hooks
- [ ] Link related repositories in the hub
"""
        path.write_text(content)

    removed = []
    for existing in output_dir.glob('*.md'):
        if existing.name == 'README.md':
            continue
        if existing.name not in current_files:
            existing.unlink()
            removed.append(existing.name)

    index_lines = [
        "# Summary Stubs",
        "",
        "Summary stub files are generated for every repository currently ranked priority 4 or 5.",
        "",
        f"Total high-priority repositories: {len(repos)}",
        f"New stubs created in this run: {len(created)}",
        f"Obsolete stubs removed in this run: {len(removed)}",
        "",
        "## Active summary files",
        "",
    ]
    for item in sorted(current_files):
        index_lines.append(f"- {item}")
    (output_dir / "README.md").write_text("\n".join(index_lines) + "\n")
    print(json.dumps({"high_priority": len(repos), "created": len(created), "removed": len(removed)}, indent=2))


if __name__ == "__main__":
    main()
