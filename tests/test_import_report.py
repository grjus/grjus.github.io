"""Check the documented briefing format and the importer's publication handoff."""

import contextlib
from datetime import datetime, timezone
import importlib.util
import io
from pathlib import Path
import re
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("import_report", ROOT / "scripts/import_report.py")
IMPORTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(IMPORTER)
EXAMPLE = (ROOT / "docs/examples/briefing.md").read_text(encoding="utf-8")


class FixedClock(datetime):
    @classmethod
    def now(cls, tz=None):
        return datetime(2027, 1, 1, tzinfo=timezone.utc).astimezone(tz)


class ReportImportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "2026-10-16_1330_deepresearch.md"

    def invoke(self, text=EXAMPLE, *, check=True, name=None, description="A factual archive preview."):
        source = self.root / name if name else self.source
        source.write_text(text, encoding="utf-8")
        args = ["import_report.py", str(source)]
        args += ["--check"] if check else ["--description", description]
        with mock.patch.object(IMPORTER, "ROOT", self.root), mock.patch.object(IMPORTER, "datetime", FixedClock), mock.patch("sys.argv", args):
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                try:
                    IMPORTER.main()
                except SystemExit as error:
                    return error.code
        return 0

    def test_documented_example_checks_without_writing(self):
        self.assertEqual(self.invoke(), 0)
        self.assertFalse((self.root / "reports").exists())
        self.assertFalse((self.root / "_posts").exists())

    def test_import_creates_synchronized_pair_and_separate_description(self):
        self.assertEqual(self.invoke(check=False), 0)
        post = self.root / "_posts/2026-10-16-1330-deepresearch.md"
        report = self.root / "reports/2026-10-16_1330_deepresearch.md"
        content = post.read_text()
        self.assertIn('title: "Independent checks strengthen agent oversight"', content)
        self.assertIn('description: "A factual archive preview."', content)
        self.assertEqual(content.split("---\n", 2)[2].lstrip(), EXAMPLE.split("\n", 1)[1].lstrip())
        self.assertEqual(report.read_text(), EXAMPLE)
        self.assertEqual(self.invoke(check=False), 0)
        self.assertEqual(self.invoke(check=False, description="Different preview."), 2)
        self.assertEqual(post.read_text(), content)

    def test_single_item_section_is_valid(self):
        reduced = EXAMPLE.split("## Azure/AWS Articles")[0]
        self.assertEqual(self.invoke(reduced), 0)

    def test_invalid_structure_is_rejected(self):
        invalid = {
            "generic title": EXAMPLE.replace("# Independent checks strengthen agent oversight", "# Deep Research: 2026-10-16 13:30", 1),
            "missing metadata": EXAMPLE.replace("- **Tags:** multi-agent systems, evaluation, agent controls\n", "", 1),
            "wrong metadata order": EXAMPLE.replace("- **Source:** Example Research Lab; fictional research preprint\n- **Date:** 2026-10-16 (published 08:00 UTC)", "- **Date:** 2026-10-16 (published 08:00 UTC)\n- **Source:** Example Research Lab; fictional research preprint"),
            "bare URL": EXAMPLE.replace("[Illustrative paper and publication record](https://example.com/research/independent-checks)", "https://example.com/research/independent-checks"),
            "legacy summary": EXAMPLE.replace("**Summary**", "**TLDR:**", 1),
            "nine bullets": EXAMPLE.replace("**Summary**\n\n", "**Summary**\n\n" + "- Extra point.\n" * 9, 1),
            "nested bullets": EXAMPLE.replace("- **Finding:**", "  - **Finding:**", 1),
            "empty section": EXAMPLE + "\n## AI/ML Articles\n",
            "placeholder": EXAMPLE + "\n### 2. Nothing notable.\n",
            "wrong numbering": EXAMPLE.replace("### 1. Independent verification", "### 2. Independent verification"),
            "unsourced overview": EXAMPLE.replace("[illustrative research paper](https://example.com/research/independent-checks)", "illustrative research paper", 1),
        }
        for name, text in invalid.items():
            with self.subTest(name=name):
                self.assertEqual(self.invoke(text), 2)

    def test_empty_report_and_over_capacity_are_rejected(self):
        self.assertEqual(self.invoke(""), 2)
        self.assertEqual(self.invoke(EXAMPLE.split("## AI/ML Articles")[0]), 2)
        prefix, rest = EXAMPLE.split("## AI/ML Articles\n\n", 1)
        item = rest.split("## Azure/AWS Articles")[0]
        oversized = prefix + "## AI/ML Articles\n\n" + "".join(
            re.sub(r"^### 1\.", f"### {number}.", item) for number in range(1, 7)
        )
        self.assertEqual(self.invoke(oversized), 2)

    def test_bad_windows_are_rejected(self):
        for text in [
            EXAMPLE.replace("2026-10-13 13:30 +02:00", "2026-10-15 13:30 +02:00"),
            EXAMPLE.replace("2026-10-16 13:30 +02:00", "2026-10-16 14:30 +02:00"),
            EXAMPLE.replace("+02:00", "+01:00"),
        ]:
            with self.subTest(window=text.splitlines()[2]):
                self.assertEqual(self.invoke(text), 2)

    def test_daylight_saving_windows_use_elapsed_hours(self):
        for start, end, name in [
            ("2026-03-26 12:30 +01:00", "2026-03-29 13:30 +02:00", "2026-03-29_1330_deepresearch.md"),
            ("2026-10-22 03:30 +02:00", "2026-10-25 02:30 +01:00", "2026-10-25_0230_deepresearch.md"),
        ]:
            text = EXAMPLE.replace("2026-10-13 13:30 +02:00", start).replace("2026-10-16 13:30 +02:00", end)
            self.assertEqual(self.invoke(text, name=name, check=False), 0)
        post = self.root / "_posts/2026-10-25-0230-deepresearch.md"
        self.assertIn('date: "2026-10-25 02:30:00 +0100"', post.read_text())

    def test_future_run_is_rejected(self):
        text = EXAMPLE.replace("2026-10-13", "2099-10-13").replace("2026-10-16", "2099-10-16")
        self.assertEqual(self.invoke(text, name="2099-10-16_1330_deepresearch.md"), 2)


if __name__ == "__main__":
    unittest.main()
