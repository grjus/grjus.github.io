"""Validate real reports and ensure each generated post matches its report."""

from datetime import datetime
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def validate_archive(root):
    reports = sorted((root / "reports").glob("*.md"))
    expected_posts = set()
    for report in reports:
        subprocess.run(
            [sys.executable, str(ROOT / "scripts/import_report.py"), str(report), "--check"],
            check=True,
        )
        day, time, _ = report.stem.split("_")
        post = root / "_posts" / f"{day}-{time}-deepresearch.md"
        expected_posts.add(post)
        if not post.is_file():
            raise ValueError(f"Missing generated post for {report.name}: {post.name}")

        raw = report.read_text(encoding="utf-8").strip() + "\n"
        generated = post.read_text(encoding="utf-8")
        parts = generated.split("---\n", 2)
        if len(parts) != 3 or parts[0] != "":
            raise ValueError(f"Invalid generated front matter: {post.name}")
        fields = {}
        for line in parts[1].splitlines():
            key, value = line.split(": ", 1)
            if key in fields:
                raise ValueError(f"Duplicate front matter key {key}: {post.name}")
            fields[key] = json.loads(value)
        required = {"title", "date", "description", "category", "report_file"}
        if set(fields) != required or not all(isinstance(value, str) for value in fields.values()):
            raise ValueError(f"Front matter must match the importer convention: {post.name}")

        window = raw.split("\n\n", 2)[1]
        end = window.split(" to ", 1)[1].removesuffix(" (Europe/Warsaw)*")
        stamp = datetime.strptime(end, "%Y-%m-%d %H:%M %z")
        if (fields["title"] != raw.splitlines()[0][2:]
                or fields["date"] != stamp.strftime("%Y-%m-%d %H:%M:%S %z")
                or fields["category"] != "Research briefing"
                or fields["report_file"] != report.name
                or not fields["description"].strip()
                or parts[2].lstrip() != raw.split("\n", 1)[1].lstrip()):
            raise ValueError(f"Post differs from its report or importer metadata: {post.name}")

    actual_posts = set((root / "_posts").glob("*.md"))
    orphaned = actual_posts - expected_posts
    if orphaned:
        raise ValueError("Posts without matching reports: " + ", ".join(sorted(path.name for path in orphaned)))
    print(f"Archive valid: {len(reports)} report/post pairs.")


def main():
    try:
        validate_archive(ROOT)
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(f"Archive validation failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
