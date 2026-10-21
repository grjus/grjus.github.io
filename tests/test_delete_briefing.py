from pathlib import Path
import tempfile
import unittest
from unittest import mock

from scripts.delete_briefing import delete_briefing


class DeleteBriefingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.report = self.root / "reports/2020-10-16_1330_deepresearch.md"
        self.post = self.root / "_posts/2020-10-16-1330-deepresearch.md"
        self.report.parent.mkdir()
        self.post.parent.mkdir()
        self.report.write_text("# A briefing\n", encoding="utf-8")
        self.post.write_text(
            '---\nreport_file: "2020-10-16_1330_deepresearch.md"\n---\n\nA briefing\n',
            encoding="utf-8",
        )

    def test_deletes_both_files_when_given_report_or_post(self):
        unrelated = self.root / "reports/other.md"
        unrelated.write_text("Keep this report")
        for selected in (self.report, self.post):
            with self.subTest(selected=selected):
                report_content, post_content = self.report.read_bytes(), self.post.read_bytes()
                self.assertEqual(delete_briefing(selected, root=self.root), (self.post, self.report))
                self.assertFalse(self.report.exists())
                self.assertFalse(self.post.exists())
                self.assertEqual(unrelated.read_text(), "Keep this report")
                self.report.write_bytes(report_content)
                self.post.write_bytes(post_content)

    def test_preview_preserves_both_files(self):
        for selected in (self.report.name, self.post.name, self.report.relative_to(self.root)):
            self.assertEqual(delete_briefing(selected, root=self.root, check=True), (self.post, self.report))
            self.assertTrue(self.report.exists())
            self.assertTrue(self.post.exists())

    def test_missing_companion_deletes_nothing(self):
        for missing, remaining in ((self.post, self.report), (self.report, self.post)):
            content = missing.read_bytes()
            missing.unlink()
            with self.assertRaisesRegex(ValueError, "Missing briefing file"):
                delete_briefing(remaining, root=self.root)
            self.assertTrue(remaining.exists())
            missing.write_bytes(content)

    def test_invalid_reference_deletes_nothing(self):
        for content in (
            '---\nreport_file: "different.md"\n---\n',
            '---\nreport_file: "2020-10-16_1330_deepresearch.md"\nreport_file: "other.md"\n---\n',
            '---\nreport_file: invalid-json\n---\n',
            'No front matter\n',
        ):
            with self.subTest(content=content):
                self.post.write_text(content)
                with self.assertRaises(ValueError):
                    delete_briefing(self.report, root=self.root)
                self.assertTrue(self.report.exists())
                self.assertEqual(self.post.read_text(), content)

    def test_paths_outside_archive_and_invalid_names_are_rejected(self):
        for selected in (
            self.root / "elsewhere" / self.report.name,
            "../" + self.report.name,
            "other.md",
            "2020-99-16_1330_deepresearch.md",
        ):
            with self.subTest(selected=selected), self.assertRaises(ValueError):
                delete_briefing(selected, root=self.root)
        self.assertTrue(self.report.exists())
        self.assertTrue(self.post.exists())

    def test_symlink_is_rejected(self):
        target = self.root / "original.md"
        self.report.rename(target)
        self.report.symlink_to(target)
        with self.assertRaises(ValueError):
            delete_briefing(self.post, root=self.root)
        self.assertTrue(target.exists())
        self.assertTrue(self.post.exists())

    def test_failed_report_deletion_restores_post(self):
        original = self.post.read_bytes()
        unlink = Path.unlink

        def fail_report(path, *args, **kwargs):
            if path == self.report:
                raise PermissionError("Report cannot be removed")
            return unlink(path, *args, **kwargs)

        with mock.patch.object(Path, "unlink", fail_report), self.assertRaises(PermissionError):
            delete_briefing(self.report, root=self.root)
        self.assertEqual(self.post.read_bytes(), original)
        self.assertTrue(self.report.exists())


if __name__ == "__main__":
    unittest.main()
