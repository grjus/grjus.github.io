#!/usr/bin/env python3
"""Turn a timestamped Markdown research report into a Jekyll post."""

import argparse
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import re
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
SECTIONS = ["Executive Summary", "AI/ML Articles", "Azure/AWS Articles", "AI/ML Repositories"]
LINK = r"\[[^\]\n]+\]\(https?://[^\s)]+\)"


def flat_bullets(text, maximum):
    lines = [line for line in text.splitlines() if line.strip()]
    return 1 <= len(lines) <= maximum and all(line.startswith("- ") and line[2:].strip() for line in lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    parser.add_argument("--description", help="One-sentence archive preview (required when importing)")
    parser.add_argument("--check", action="store_true", help="Validate only; do not write any files")
    args = parser.parse_args()
    if not args.check and not (args.description and args.description.strip()):
        parser.error("--description is required when importing; it is the preview, not the title")
    match = re.fullmatch(r"(\d{4}-\d{2}-\d{2})_(\d{4})_deepresearch\.md", args.report.name)
    if not match:
        parser.error("Expected YYYY-MM-DD_HHMM_deepresearch.md")
    try:
        stamp = datetime.strptime(" ".join(match.groups()), "%Y-%m-%d %H%M")
        raw = args.report.read_text(encoding="utf-8").strip() + "\n"
    except (ValueError, OSError) as error:
        parser.error(str(error))
    heading = re.fullmatch(r"# (\S.*)", raw.splitlines()[0])
    if not heading:
        parser.error("Expected a descriptive report title as the first Markdown heading")
    title = heading.group(1).strip()
    if re.search(r"\d{4}-\d{2}-\d{2}|\b\d{1,2}:\d{2}\b", title) or title.lower().startswith("deep research"):
        parser.error("Use a findings-led title; keep the run date in the filename and window")
    window_pattern = r"\*Window: (\d{4}-\d{2}-\d{2} \d{2}:\d{2} [+-]\d{2}:\d{2}) to (\d{4}-\d{2}-\d{2} \d{2}:\d{2} [+-]\d{2}:\d{2}) \(Europe/Warsaw\)\*"
    window = re.fullmatch(window_pattern, raw.split("\n\n", 2)[1] if "\n\n" in raw else "")
    if not window:
        parser.error("Expected the exact Window line after the title, with explicit UTC offsets")
    try:
        start, end = [datetime.strptime(value, "%Y-%m-%d %H:%M %z") for value in window.groups()]
    except ValueError as error:
        parser.error(str(error))
    warsaw = ZoneInfo("Europe/Warsaw")
    if any(point.utcoffset() != point.astimezone(warsaw).utcoffset() for point in [start, end]):
        parser.error("Window offsets must match Europe/Warsaw at each endpoint")
    if end.astimezone(timezone.utc) - start.astimezone(timezone.utc) != timedelta(hours=72):
        parser.error("Window must cover exactly 72 elapsed hours")
    if end.replace(tzinfo=None) != stamp:
        parser.error("Window end must match the filename's local run time")
    stamp = end.astimezone(warsaw)
    if stamp > datetime.now(warsaw):
        parser.error("Report date must not be in the future")
    sections = re.findall(r"^## (.+)$", raw, re.M)
    if (len(sections) < 2 or sections[0] != SECTIONS[0]
            or sections != [name for name in SECTIONS if name in sections]):
        parser.error("Expected Executive Summary followed by qualifying item sections in the documented order")
    for section in re.finditer(r"^## ([^\n]+)\n(.*?)(?=^## |\Z)", raw, re.M | re.S):
        name, text = section.groups()
        if name == SECTIONS[0]:
            if not flat_bullets(text, 5) or any(not re.search(LINK, line) for line in text.strip().splitlines() if line.strip()):
                parser.error("Executive Summary must contain 1–5 flat bullets, each with a source link")
            continue
        headings = re.findall(r"^### (.+)$", text, re.M)
        entries = re.findall(r"^### (\d+)\. .+$", text, re.M)
        maximum = 5 if name == "AI/ML Articles" else 2
        if not 1 <= len(entries) <= maximum or len(entries) != len(headings):
            parser.error(f"{name} must contain 1–{maximum} items; omit empty sections")
        if entries != [str(number) for number in range(1, len(entries) + 1)]:
            parser.error(f"Number items consecutively in {name}")
        if text.split("### ", 1)[0].strip():
            parser.error(f"Start {name} with its first item; do not add section filler")
        for item in re.finditer(r"^### ([^\n]+)\n(.*?)(?=^### |\Z)", text, re.M | re.S):
            metadata = item.group(2).split("**Summary**", 1)[0]
            fields = re.findall(r"^- \*\*([^*\n]+):\*\* (.+)$", metadata, re.M)
            expected = (["Stars", "Language", "License", "Last commit", "Link"]
                        if name == "AI/ML Repositories" else ["Source", "Date", "Tags", "Link"])
            if [field for field, value in fields] != expected or len(metadata.strip().splitlines()) != len(expected):
                parser.error(f"Expected metadata fields {', '.join(expected)} for: {item.group(1)}")
            if not re.fullmatch(LINK, fields[-1][1]):
                parser.error(f"Link must be a descriptive HTTP(S) Markdown link for: {item.group(1)}")
    if len(re.findall(r"^# ", raw, re.M)) != 1:
        parser.error("Expected exactly one report title")
    if re.search(r"^#{4,} ", raw, re.M):
        parser.error("Do not add headings below the item level")
    for item in re.finditer(r"^### ([^\n]+)\n(.*?)(?=^## |^### |\Z)", raw, re.M | re.S):
        summary = item.group(2).split("**Summary**\n\n")
        if len(summary) != 2:
            parser.error(f"Expected one Summary bullet list for: {item.group(1)}")
        if not flat_bullets(summary[1], 8):
            parser.error(f"Summary must contain 1–8 bullet points for: {item.group(1)}")
    if args.check:
        print(f"Valid report: {args.report}")
        return
    body = raw.split("\n", 1)[1].lstrip()
    metadata = {
        "title": title,
        "date": stamp.strftime("%Y-%m-%d %H:%M:%S %z"),
        "description": args.description,
        "category": "Research briefing",
        "report_file": args.report.name,
    }
    front_matter = "---\n" + "".join(f"{key}: {json.dumps(value)}\n" for key, value in metadata.items()) + "---\n\n"
    archive = ROOT / "reports" / args.report.name
    post = ROOT / "_posts" / f"{stamp:%Y-%m-%d-%H%M}-deepresearch.md"
    archive.parent.mkdir(exist_ok=True)
    post.parent.mkdir(exist_ok=True)
    for path, content in [(archive, raw), (post, front_matter + body)]:
        if path.exists() and path.read_text(encoding="utf-8") != content:
            parser.error(f"Refusing to overwrite different content: {path}")
    archive.write_text(raw, encoding="utf-8")
    post.write_text(front_matter + body, encoding="utf-8")
    print(post)


if __name__ == "__main__":
    main()
