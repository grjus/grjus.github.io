#!/usr/bin/env python3
"""Delete a briefing's generated post and original Markdown report together."""

import argparse
from datetime import datetime
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]


def delete_briefing(briefing, *, root=ROOT, check=False):
    root = root.resolve()
    briefing = Path(briefing)
    report_match = re.fullmatch(r"(\d{4}-\d{2}-\d{2})_(\d{4})_deepresearch\.md", briefing.name)
    post_match = re.fullmatch(r"(\d{4}-\d{2}-\d{2})-(\d{4})-deepresearch\.md", briefing.name)
    match = report_match or post_match
    if not match:
        raise ValueError("Expected a timestamped briefing report or generated post filename")
    day, time = match.groups()
    datetime.strptime(f"{day} {time}", "%Y-%m-%d %H%M")
    report = root / "reports" / f"{day}_{time}_deepresearch.md"
    post = root / "_posts" / f"{day}-{time}-deepresearch.md"
    selected = report if report_match else post
    supplied = selected if briefing.parent == Path(".") else root / briefing
    if supplied.resolve() != selected:
        raise ValueError("Briefing must be inside this repository's reports/ or _posts/ directory")

    # Check both files and the reference before removing either file.
    for path in (report, post):
        if path.is_symlink() or path.parent.resolve() != path.parent:
            raise ValueError(f"Refusing to delete a briefing through a symbolic link: {path}")
        if not path.is_file():
            raise ValueError(f"Missing briefing file; nothing deleted: {path}")
    post_content = post.read_bytes()
    parts = post_content.decode("utf-8").split("---\n", 2)
    if len(parts) != 3 or parts[0] != "":
        raise ValueError("Invalid post front matter; nothing deleted")
    references = re.findall(r"^report_file: (.+)$", parts[1], re.M)
    if len(references) != 1 or json.loads(references[0]) != report.name:
        raise ValueError("Post does not reference the matching report; nothing deleted")

    if not check:
        post.unlink()
        try:
            report.unlink()
        except OSError:
            # Restore the post if removing the report fails.
            post.write_bytes(post_content)
            raise
    return post, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("briefing", type=Path, help="Report or post filename/path within this repository")
    parser.add_argument("--check", action="store_true", help="Preview the two files without deleting them")
    args = parser.parse_args()
    try:
        paths = delete_briefing(args.briefing, check=args.check)
    except (ValueError, OSError) as error:
        print(f"Cannot delete briefing: {error}", file=sys.stderr)
        return 1
    for path in paths:
        print(f"{'Would delete' if args.check else 'Deleted'}: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
