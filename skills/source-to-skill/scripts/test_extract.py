#!/usr/bin/env python3
"""Regression tests for source-to-skill extraction helper."""

from __future__ import annotations

import importlib.util
import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


sys.dont_write_bytecode = True

SCRIPT_DIR = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("source_to_skill_extract", SCRIPT_DIR / "extract.py")
assert SPEC is not None and SPEC.loader is not None
extract = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = extract
SPEC.loader.exec_module(extract)


def quiet_write_outputs(files: list[Path], output_dir: Path, mode: str, input_warnings: list[object] | None = None, strict: bool = False) -> int:
    with contextlib.redirect_stdout(io.StringIO()):
        return extract.write_outputs(files, output_dir, mode, input_warnings, strict)


class ExtractorTests(unittest.TestCase):
    def test_markdown_preserves_code_indentation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "source.md"
            source.write_text("```python\ndef f():\n    return 1\n```\n", encoding="utf-8")

            exit_code = quiet_write_outputs([source], root / "out", "technical")
            full_text = (root / "out" / "full_text.md").read_text(encoding="utf-8")

            self.assertEqual(exit_code, 0)
            self.assertIn("    return 1", full_text)
            self.assertIn("<!-- EXTRACTION status=ok", full_text)

    def test_metadata_records_extractor_run_information(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "source.md"
            source.write_text("Useful text", encoding="utf-8")

            exit_code = quiet_write_outputs([source], root / "out", "text")
            metadata = json.loads((root / "out" / "metadata.json").read_text(encoding="utf-8"))

            self.assertEqual(exit_code, 0)
            self.assertEqual(metadata["schema_version"], extract.METADATA_SCHEMA_VERSION)
            self.assertEqual(metadata["extractor_version"], extract.EXTRACTOR_VERSION)
            self.assertIn("generated_at_utc", metadata)
            self.assertIn("python_version", metadata)
            self.assertIn("platform", metadata)

    def test_default_output_dir_is_unique_without_env_override(self) -> None:
        original = os.environ.pop("SOURCE_SKILL_WORKDIR", None)
        first: Path | None = None
        second: Path | None = None
        try:
            first = extract.default_output_dir()
            second = extract.default_output_dir()

            self.assertNotEqual(first, second)
            self.assertTrue(first.name.startswith("source_skill_work_"))
            self.assertTrue(second.name.startswith("source_skill_work_"))
            self.assertTrue(first.exists())
            self.assertTrue(second.exists())
        finally:
            if original is not None:
                os.environ["SOURCE_SKILL_WORKDIR"] = original
            for path in (first, second):
                if path is not None:
                    shutil.rmtree(path, ignore_errors=True)

    def test_default_output_dir_honors_env_override(self) -> None:
        original = os.environ.get("SOURCE_SKILL_WORKDIR")
        try:
            os.environ["SOURCE_SKILL_WORKDIR"] = "/tmp/source_skill_work_fixed"

            self.assertEqual(extract.default_output_dir(), Path("/tmp/source_skill_work_fixed"))
        finally:
            if original is None:
                os.environ.pop("SOURCE_SKILL_WORKDIR", None)
            else:
                os.environ["SOURCE_SKILL_WORKDIR"] = original

    def test_html_strips_script_content(self) -> None:
        text = extract.extract_html_text("<h1>Hello</h1><script>secret()</script><p>Visible</p>")

        self.assertIn("Hello", text)
        self.assertIn("Visible", text)
        self.assertNotIn("secret", text)

    def test_form_feeds_become_page_break_markers(self) -> None:
        text = extract.normalize_text("First page\fSecond page")

        self.assertIn("<!-- PAGE BREAK -->", text)
        self.assertNotIn("\f", text)

    def test_epub_with_dotted_package_path_extracts_spine_text(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            epub = root / "sample.epub"
            with zipfile.ZipFile(epub, "w") as archive:
                archive.writestr(
                    "META-INF/container.xml",
                    """<?xml version="1.0"?>
<container xmlns="urn:oasis:names:tc:opendocument:xmlns:container" version="1.0">
  <rootfiles><rootfile full-path="OEBPS.v1/content.opf" media-type="application/oebps-package+xml"/></rootfiles>
</container>""",
                )
                archive.writestr(
                    "OEBPS.v1/content.opf",
                    """<package xmlns="http://www.idpf.org/2007/opf" version="3.0">
  <manifest><item id="ch1" href="chapter1.xhtml" media-type="application/xhtml+xml"/></manifest>
  <spine><itemref idref="ch1"/></spine>
</package>""",
                )
                archive.writestr("OEBPS.v1/chapter1.xhtml", "<html><body><p>EPUB text.</p></body></html>")

            text, method = extract.read_epub(epub)

            self.assertEqual(method, "epub-stdlib")
            self.assertIn("EPUB text.", text)

    def test_empty_extraction_is_not_successful(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "empty.md"
            source.write_text("", encoding="utf-8")

            exit_code = quiet_write_outputs([source], root / "out", "text")
            metadata = json.loads((root / "out" / "metadata.json").read_text(encoding="utf-8"))

            self.assertEqual(exit_code, 1)
            self.assertEqual(metadata["successful_sources"], 0)
            self.assertEqual(metadata["failed_sources"], 1)
            self.assertEqual(metadata["sources"][0]["status"], "empty")
            self.assertEqual(metadata["sources"][0]["page_breaks"], 0)
            self.assertRegex(metadata["sources"][0]["sha256"], r"^[0-9a-f]{64}$")

    def test_archive_member_limit_blocks_large_archives(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            archive_path = root / "many.docx"
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr("word/document.xml", "<w:document />")
                archive.writestr("word/header1.xml", "<w:hdr />")

            original_limit = extract.MAX_ARCHIVE_MEMBERS
            extract.MAX_ARCHIVE_MEMBERS = 1
            try:
                with self.assertRaisesRegex(ValueError, "too many files"):
                    extract.read_docx(archive_path)
            finally:
                extract.MAX_ARCHIVE_MEMBERS = original_limit

    def test_input_warnings_are_recorded_and_strict_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "source.md"
            source.write_text("Useful text", encoding="utf-8")
            unsupported = root / "source.bin"
            unsupported.write_bytes(b"binary")

            files, warnings = extract.resolve_inputs([str(source), str(unsupported), str(root / "missing.md")])
            exit_code = quiet_write_outputs(files, root / "out", "text", warnings, strict=True)
            metadata = json.loads((root / "out" / "metadata.json").read_text(encoding="utf-8"))

            self.assertEqual(exit_code, 1)
            self.assertEqual(len(files), 1)
            self.assertEqual(len(warnings), 2)
            self.assertEqual(len(metadata["input_warnings"]), 2)

    def test_source_size_limit_marks_source_failed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "too-large.md"
            source.write_text("1234567890", encoding="utf-8")

            original_limit = extract.MAX_SOURCE_BYTES
            extract.MAX_SOURCE_BYTES = 5
            try:
                exit_code = quiet_write_outputs([source], root / "out", "text")
                metadata = json.loads((root / "out" / "metadata.json").read_text(encoding="utf-8"))
            finally:
                extract.MAX_SOURCE_BYTES = original_limit

            self.assertEqual(exit_code, 1)
            self.assertEqual(metadata["sources"][0]["status"], "failed")
            self.assertIn("too large", metadata["sources"][0]["warning"])
            self.assertIsNone(metadata["sources"][0]["sha256"])

    def test_list_mode_reports_sources_and_warnings_without_extracting(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "source.md"
            source.write_text("Useful text", encoding="utf-8")
            unsupported = root / "source.bin"
            unsupported.write_bytes(b"binary")

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_DIR / "extract.py"),
                    str(source),
                    str(unsupported),
                    str(root / "missing.md"),
                    "--list",
                ],
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            payload = json.loads(result.stdout)

            self.assertEqual(result.returncode, 0)
            self.assertEqual(payload["schema_version"], extract.METADATA_SCHEMA_VERSION)
            self.assertEqual(payload["extractor_version"], extract.EXTRACTOR_VERSION)
            self.assertEqual(payload["total_sources"], 1)
            self.assertEqual(len(payload["input_warnings"]), 2)
            self.assertEqual(payload["sources"][0]["name"], "source.md")

    def test_metadata_records_full_text_line_ranges(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            first = root / "first.md"
            second = root / "second.md"
            first.write_text("First text", encoding="utf-8")
            second.write_text("Second text", encoding="utf-8")

            exit_code = quiet_write_outputs([first, second], root / "out", "text")
            full_text = (root / "out" / "full_text.md").read_text(encoding="utf-8")
            metadata = json.loads((root / "out" / "metadata.json").read_text(encoding="utf-8"))

            self.assertEqual(exit_code, 0)
            lines = full_text.splitlines()
            first_source = metadata["sources"][0]
            second_source = metadata["sources"][1]
            self.assertEqual(first_source["source_index"], 1)
            self.assertEqual(second_source["source_index"], 2)
            self.assertIn("SOURCE 1 START", lines[first_source["full_text_start_line"] - 1])
            self.assertIn("SOURCE 1 END", lines[first_source["full_text_end_line"] - 1])
            self.assertIn("SOURCE 2 START", lines[second_source["full_text_start_line"] - 1])
            self.assertIn("SOURCE 2 END", lines[second_source["full_text_end_line"] - 1])


if __name__ == "__main__":
    unittest.main()