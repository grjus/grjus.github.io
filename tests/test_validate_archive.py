import contextlib
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.validate_archive import validate_archive

ROOT = Path(__file__).resolve().parents[1]


class ArchiveValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "reports").mkdir()
        (self.root / "_posts").mkdir()

    def add_pair(self):
        report = self.root / "reports/2020-10-16_1330_deepresearch.md"
        text = (ROOT / "docs/examples/briefing.md").read_text().replace("2026-", "2020-")
        report.write_text(text)
        # Import into a temporary copy so the real archive is never changed.
        script = self.root / "scripts/import_report.py"
        script.parent.mkdir()
        script.write_text((ROOT / "scripts/import_report.py").read_text())
        subprocess.run([sys.executable, str(script), str(report), "--description", "An example preview."],
                       check=True, capture_output=True)
        return report, self.root / "_posts/2020-10-16-1330-deepresearch.md"

    def validate(self):
        with contextlib.redirect_stdout(io.StringIO()):
            validate_archive(self.root)

    def test_empty_archive_is_valid(self):
        self.validate()

    def test_matching_pair_is_valid(self):
        self.add_pair()
        self.validate()

    def test_missing_post_is_rejected(self):
        _, post = self.add_pair()
        post.unlink()
        with self.assertRaisesRegex(ValueError, "Missing generated post"):
            self.validate()

    def test_orphan_post_is_rejected(self):
        report, _ = self.add_pair()
        report.unlink()
        with self.assertRaisesRegex(ValueError, "Posts without matching reports"):
            self.validate()

    def test_mismatched_post_is_rejected(self):
        _, post = self.add_pair()
        original = post.read_text()
        for text in [
            original.replace("fictional study compares", "fictional study examines", 1),
            original.replace("Independent checks strengthen agent oversight", "A different headline", 1),
            original.replace("2020-10-16 13:30:00 +0200", "2020-10-16 14:30:00 +0200"),
            original.replace('description: "An example preview."', 'description: ""'),
            original.replace("2020-10-16_1330_deepresearch.md", "wrong-file.md"),
            original + "Extra content.\n",
        ]:
            with self.subTest(text=text[:100]):
                post.write_text(text)
                with self.assertRaisesRegex(ValueError, "Post differs"):
                    self.validate()


if __name__ == "__main__":
    unittest.main()
