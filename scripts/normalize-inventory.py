#!/usr/bin/env python3
import argparse
import csv
import json
import re
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

CATEGORY_PATTERNS = {
    "ai-ml": ["ai", "ml", "gpt", "llm", "claude", "openai", "copilot", "agent", "rag", "vector"],
    "automation": ["automation", "workflow", "action", "bot", "script", "pipeline", "orchestr"],
    "infrastructure": ["infra", "terraform", "k8s", "kubernetes", "docker", "helm", "aws", "gcp", "azure", "iac"],
    "devtools": ["devtool", "cli", "vscode", "ide", "debug", "sdk", "extension", "plugin", "terminal"],
    "web-app": ["app", "web", "ui", "dashboard", "site"],
    "api-backend": ["api", "backend", "server", "microservice", "service"],
    "frontend": ["frontend", "react", "vue", "nextjs", "next.js", "svelte", "angular"],
    "data": ["data", "dataset", "etl", "analytics", "sql", "db", "warehouse"],
    "docs": ["docs", "documentation", "guide", "tutorial", "awesome", "resources", "readme"],
    "experiment": ["experiment", "prototype", "demo", "sample", "lab", "playground", "example", "test"],
}

INDEX_ORDER = [
    "ai-ml",
    "automation",
    "infrastructure",
    "devtools",
    "web-app",
    "api-backend",
    "frontend",
    "data",
    "docs",
    "experiment",
    "fork-reference",
    "empty-low-signal",
    "unknown",
]


def load_json_items(path_str):
    path = Path(path_str)
    data = json.loads(path.read_text())
    if isinstance(data, dict):
        return data.get("items", [])
    if isinstance(data, list):
        return data
    raise ValueError(f"Unsupported JSON shape in {path}")


def merge_repo(existing, new):
    merged = dict(existing)
    for key, value in new.items():
        if key not in merged or merged[key] in (None, "", [], {}):
            merged[key] = value
            continue
        if key in {"topics", "repositoryTopics"}:
            continue
        if key in {"updatedAt", "updated_at"}:
            if str(value) > str(merged[key]):
                merged[key] = value
        if key == "size":
            try:
                merged[key] = max(int(merged.get(key) or 0), int(value or 0))
            except Exception:
                pass
    return merged


def name_with_owner(repo):
    return repo.get("nameWithOwner") or repo.get("full_name") or repo.get("fullName") or repo.get("name")


def repo_url(repo):
    return repo.get("url") if str(repo.get("url", "")).startswith("https://github.com/") else repo.get("html_url") or repo.get("url") or ""


def primary_language(repo):
    value = repo.get("primaryLanguage")
    if isinstance(value, dict):
        return value.get("name") or ""
    return repo.get("language") or value or ""


def extract_topics(repo):
    topics = []
    raw_topics = repo.get("topics")
    if isinstance(raw_topics, list):
        topics.extend(t for t in raw_topics if isinstance(t, str) and t)
    raw_repo_topics = repo.get("repositoryTopics")
    if isinstance(raw_repo_topics, list):
        for entry in raw_repo_topics:
            if isinstance(entry, str) and entry:
                topics.append(entry)
            elif isinstance(entry, dict):
                topic = entry.get("topic")
                if isinstance(topic, dict) and topic.get("name"):
                    topics.append(topic["name"])
                elif entry.get("name"):
                    topics.append(entry["name"])
    deduped = sorted({t.strip() for t in topics if str(t).strip()})
    return deduped


def parse_dt(value):
    if not value:
        return None
    value = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def slugify(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def build_text_index(repo_name, description, topics):
    normalized = " ".join([repo_name, description, " ".join(topics)]).lower()
    normalized = re.sub(r"[^a-z0-9.+#]+", " ", normalized)
    tokens = set(normalized.split())
    return normalized, tokens


def matches_needle(normalized, tokens, needle):
    if re.fullmatch(r"[a-z0-9+#.-]+", needle):
        return needle in tokens
    return needle in normalized


def updated_sort_value(value):
    parsed = parse_dt(value)
    if not parsed:
        return ""
    return parsed.isoformat()


def sort_key(repo):
    return (
        repo["priority"],
        repo["status"] == "active",
        not repo["isFork"],
        updated_sort_value(repo["lastUpdated"]),
        repo["nameWithOwner"].lower(),
    )


def infer_status(is_archived, size, updated_at):
    if is_archived:
        return "archived"
    if size == 0:
        return "empty"
    parsed = parse_dt(updated_at)
    if parsed and parsed < datetime.now(timezone.utc) - timedelta(days=365) and size < 100:
        return "stale"
    if updated_at:
        return "active"
    return "unknown"


def infer_classification(repo_name, description, topics, is_fork, size):
    normalized, tokens = build_text_index(repo_name, description, topics)
    classes = set()
    for category, needles in CATEGORY_PATTERNS.items():
        if any(matches_needle(normalized, tokens, needle) for needle in needles):
            classes.add(category)
    if is_fork:
        classes.add("fork-reference")
    if size == 0:
        classes.add("empty-low-signal")
    if not classes:
        classes.add("unknown")
    ordered = [category for category in INDEX_ORDER if category in classes]
    extras = sorted(classes.difference(ordered))
    return ordered + extras


def infer_priority(repo, classes, status):
    is_fork = repo["isFork"]
    size = repo["size"]
    description = repo["description"]
    language = repo["primaryLanguage"]
    updated_at = repo["lastUpdated"]
    parsed = parse_dt(updated_at)
    recent = bool(parsed and parsed >= datetime.now(timezone.utc) - timedelta(days=180))

    priority = 2
    if is_fork:
        priority = 1 if size == 0 and not description else 2
    else:
        priority = 2

    if not is_fork and size == 0:
        priority = 1
    if "empty-low-signal" in classes:
        priority = min(priority, 1 if size == 0 else 2)
    if status == "archived":
        priority = max(priority, 2) if any(c in classes for c in {"ai-ml", "automation", "infrastructure", "devtools"}) and size > 300 else 1
    if status == "stale":
        priority = min(priority, 2)
    if not is_fork and language and size > 100:
        priority = max(priority, 3)
    if not is_fork and language and size > 1000:
        priority = max(priority, 4)
    if not is_fork and any(c in classes for c in {"ai-ml", "automation", "infrastructure", "devtools", "web-app", "api-backend"}) and recent:
        priority = max(priority, 4)
    if not is_fork and any(c in classes for c in {"ai-ml", "automation", "infrastructure", "devtools"}) and size > 3000:
        priority = max(priority, 5)
    if not is_fork and any(c in classes for c in {"docs", "data"}) and size > 1500:
        priority = max(priority, 4)
    if is_fork and size > 1000 and description:
        priority = max(priority, 2)
    return max(1, min(priority, 5))


def infer_why_useful(repo):
    classes = repo["classification"]
    if repo["priority"] >= 5:
        return "High-signal original repository with active engineering value for AI, automation, infrastructure, or developer tooling review."
    if repo["priority"] == 4:
        return "Strong candidate for detailed review because it appears to contain meaningful code, docs, or reusable implementation patterns."
    if repo["status"] == "archived":
        return "Archived snapshot that may still provide historical patterns, naming ideas, or reference code."
    if repo["isFork"]:
        return "Useful mainly as upstream reference material or dependency context rather than as a core owned project."
    if "docs" in classes:
        return "Likely useful as a curated knowledge or documentation resource."
    if repo["status"] == "empty":
        return "Low current value because the repository appears empty or minimally populated."
    return "Potentially useful after manual review to confirm scope, quality, and relationship to adjacent repositories."


def infer_next_action(repo):
    if repo["priority"] >= 5:
        return "Create a detailed repo summary, inspect code structure, and identify reusable assets or connector candidates."
    if repo["priority"] == 4:
        return "Review README and top-level files, then decide whether to promote into the top-20 connector set."
    if repo["status"] in {"archived", "stale", "empty"}:
        return "Defer deep review unless it becomes relevant to a specific investigation."
    if repo["isFork"]:
        return "Keep as reference only; compare against upstream before spending more time."
    return "Queue for a lightweight manual pass and verify whether it belongs in a stronger category."


def normalize_record(repo):
    repo_name = name_with_owner(repo)
    description = (repo.get("description") or "").strip()
    topics = extract_topics(repo)
    last_updated = repo.get("updatedAt") or repo.get("updated_at") or ""
    visibility = repo.get("visibility") or ("private" if repo.get("isPrivate") or repo.get("private") else "public")
    language = primary_language(repo)
    is_fork = bool(repo.get("isFork") if repo.get("isFork") is not None else repo.get("fork"))
    is_archived = bool(repo.get("isArchived") if repo.get("isArchived") is not None else repo.get("archived"))
    size = int(repo.get("size") or repo.get("diskUsage") or 0)
    status = infer_status(is_archived, size, last_updated)
    classification = infer_classification(repo_name or "", description, topics, is_fork, size)

    record = {
        "nameWithOwner": repo_name or "",
        "url": repo_url(repo),
        "isFork": is_fork,
        "visibility": visibility or "unknown",
        "description": description,
        "primaryLanguage": language,
        "topics": topics,
        "lastUpdated": last_updated,
        "classification": classification,
        "priority": 1,
        "status": status,
        "whyUseful": "",
        "recommendedNextAction": "",
        "isArchived": is_archived,
        "size": size,
    }
    record["priority"] = infer_priority(record, classification, status)
    record["whyUseful"] = infer_why_useful(record)
    record["recommendedNextAction"] = infer_next_action(record)
    return record


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, sort_keys=False) + "\n")


def write_csv(path, inventory):
    fields = [
        "nameWithOwner",
        "url",
        "isFork",
        "visibility",
        "description",
        "primaryLanguage",
        "topics",
        "lastUpdated",
        "classification",
        "priority",
        "status",
        "whyUseful",
        "recommendedNextAction",
    ]
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for row in inventory:
            row = dict(row)
            row["topics"] = "|".join(row["topics"])
            row["classification"] = "|".join(row["classification"])
            writer.writerow({field: row[field] for field in fields})


def build_maps(inventory):
    topics = defaultdict(list)
    languages = defaultdict(list)
    clusters = defaultdict(list)
    for repo in inventory:
        for topic in repo["topics"]:
            topics[topic].append(repo["nameWithOwner"])
        languages[repo["primaryLanguage"] or "unknown"].append(repo["nameWithOwner"])
        for category in repo["classification"]:
            clusters[category].append(repo["nameWithOwner"])
    for mapping in (topics, languages, clusters):
        for key in mapping:
            mapping[key] = sorted(set(mapping[key]))
    return topics, languages, clusters


def build_recommendations(inventory):
    useful_forks = sorted(
        [r for r in inventory if r["isFork"] and r["priority"] >= 2],
        key=sort_key,
        reverse=True,
    )[:25]
    top_ranked = sorted(inventory, key=sort_key, reverse=True)
    top20 = top_ranked[:20]
    top50 = top_ranked[:50]
    skip = sorted([r for r in inventory if r["priority"] == 1], key=sort_key, reverse=True)[:50]

    lines = [
        "# Recommended ChatGPT Connector Selection",
        "",
        "This index highlights the repositories most worth connecting first for repository-aware assistants and research workflows.",
        "",
        "## Top 20 repos to connect first",
        "",
    ]
    for repo in top20:
        lines.append(f"- **{repo['nameWithOwner']}** — P{repo['priority']} — {repo['whyUseful']}")
    lines.extend(["", "## Top 50 broader candidate set", ""])
    for repo in top50:
        lines.append(f"- **{repo['nameWithOwner']}** — {repo['status']} — {', '.join(repo['classification'])}")
    lines.extend(["", "## Repos to skip by default", ""])
    for repo in skip:
        lines.append(f"- **{repo['nameWithOwner']}** — {repo['status']} — {repo['recommendedNextAction']}")
    lines.extend(["", "## Useful forks", ""])
    for repo in useful_forks:
        lines.append(f"- **{repo['nameWithOwner']}** — {repo['description'] or 'No description provided.'}")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Normalize repository data into Repo Intelligence Hub outputs.")
    parser.add_argument("--input", action="append", dest="inputs", help="Input JSON file(s). Accepts GitHub search API payloads or list payloads.")
    parser.add_argument("--output-dir", default="repos")
    parser.add_argument("--indexes-dir", default="indexes")
    args = parser.parse_args()

    inputs = args.inputs or ["repos/raw-gh-output.json"]
    merged = {}
    for path in inputs:
        for repo in load_json_items(path):
            key = name_with_owner(repo)
            if not key:
                continue
            merged[key] = merge_repo(merged.get(key, {}), repo)

    inventory = [normalize_record(repo) for repo in merged.values()]
    inventory.sort(key=sort_key, reverse=True)

    repos_dir = Path(args.output_dir)
    indexes_dir = Path(args.indexes_dir)
    repos_dir.mkdir(parents=True, exist_ok=True)
    indexes_dir.mkdir(parents=True, exist_ok=True)

    public_inventory = [
        {key: value for key, value in repo.items() if key not in {"isArchived", "size"}}
        for repo in inventory
    ]
    write_json(repos_dir / "inventory.json", public_inventory)
    write_csv(repos_dir / "inventory.csv", public_inventory)
    write_json(repos_dir / "originals.json", [r for r in public_inventory if not r["isFork"]])
    write_json(repos_dir / "forks.json", [r for r in public_inventory if r["isFork"]])
    write_json(repos_dir / "archived-or-stale.json", [r for r in public_inventory if r["status"] in {"archived", "stale"}])
    write_json(repos_dir / "high-priority.json", [r for r in public_inventory if r["priority"] >= 4])

    ranking = sorted(public_inventory, key=sort_key, reverse=True)
    topics, languages, clusters = build_maps(public_inventory)
    write_json(indexes_dir / "priority-ranking.json", ranking)
    write_json(indexes_dir / "topic-map.json", dict(sorted(topics.items())))
    write_json(indexes_dir / "language-map.json", dict(sorted(languages.items())))
    write_json(indexes_dir / "repo-clusters.json", {key: clusters.get(key, []) for key in INDEX_ORDER if key in clusters})
    (indexes_dir / "recommended-chatgpt-connector-selection.md").write_text(build_recommendations(public_inventory))

    stats = {
        "total": len(public_inventory),
        "originals": sum(1 for r in public_inventory if not r["isFork"]),
        "forks": sum(1 for r in public_inventory if r["isFork"]),
        "archived_or_stale": sum(1 for r in public_inventory if r["status"] in {"archived", "stale"}),
        "high_priority": sum(1 for r in public_inventory if r["priority"] >= 4),
        "priority_5": sum(1 for r in public_inventory if r["priority"] == 5),
        "priority_4": sum(1 for r in public_inventory if r["priority"] == 4),
        "priority_3": sum(1 for r in public_inventory if r["priority"] == 3),
        "priority_1_2": sum(1 for r in public_inventory if r["priority"] <= 2),
    }
    write_json(repos_dir / "_summary-stats.json", stats)
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
