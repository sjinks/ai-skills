#!/usr/bin/env python3
"""Extract readable text from source files for source-to-skill workflows.

This helper is intentionally conservative:
- it uses the Python standard library for text, HTML, RTF, DOCX, and EPUB;
- it uses external converters only when already installed;
- it never installs packages or executes content from source documents.
"""

from __future__ import annotations

import argparse
import datetime
import glob
import hashlib
import html
import html.parser
import json
import os
import platform
import posixpath
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
import zipfile
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree


TEXT_EXTENSIONS = {".txt", ".md", ".markdown", ".rst", ".adoc"}
HTML_EXTENSIONS = {".html", ".htm"}
DOCX_EXTENSIONS = {".docx"}
EPUB_EXTENSIONS = {".epub"}
PDF_EXTENSIONS = {".pdf"}
RTF_EXTENSIONS = {".rtf"}
EBOOK_EXTENSIONS = {".mobi", ".azw", ".azw3"}

SUPPORTED_EXTENSIONS = (
    TEXT_EXTENSIONS
    | HTML_EXTENSIONS
    | DOCX_EXTENSIONS
    | EPUB_EXTENSIONS
    | PDF_EXTENSIONS
    | RTF_EXTENSIONS
    | EBOOK_EXTENSIONS
)

EXTRACTOR_VERSION = "0.2.0"
METADATA_SCHEMA_VERSION = 2

MAX_ARCHIVE_MEMBERS = int(os.environ.get("SOURCE_SKILL_MAX_ARCHIVE_MEMBERS", "2000"))
MAX_ARCHIVE_ENTRY_BYTES = int(os.environ.get("SOURCE_SKILL_MAX_ARCHIVE_ENTRY_BYTES", str(20 * 1024 * 1024)))
MAX_ARCHIVE_TOTAL_BYTES = int(os.environ.get("SOURCE_SKILL_MAX_ARCHIVE_TOTAL_BYTES", str(100 * 1024 * 1024)))
MAX_SOURCE_BYTES = int(os.environ.get("SOURCE_SKILL_MAX_SOURCE_BYTES", str(200 * 1024 * 1024)))


@dataclass
class SourceMetadata:
    path: str
    resolved_path: str
    name: str
    format: str
    bytes: int
    sha256: str | None
    characters: int
    words: int
    estimated_tokens: int
    page_breaks: int
    method: str
    status: str
    warning: str | None = None
    source_index: int | None = None
    full_text_start_line: int | None = None
    full_text_end_line: int | None = None


@dataclass
class InputWarning:
    input: str
    reason: str


class TextExtractor(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "noscript"}:
            self.skip_depth += 1
        if tag in {"p", "br", "div", "section", "article", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6"}:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript"} and self.skip_depth:
            self.skip_depth -= 1
        if tag in {"p", "div", "section", "article", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self.skip_depth:
            self.parts.append(data)

    def text(self) -> str:
        return normalize_text("".join(self.parts))


def normalize_text(value: str) -> str:
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    value = value.replace("\f", "\n\n<!-- PAGE BREAK -->\n\n")
    value = "\n".join(line.rstrip() for line in value.split("\n"))
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value.strip()


def read_text(path: Path) -> tuple[str, str]:
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return normalize_text(path.read_text(encoding=encoding)), f"text:{encoding}"
        except UnicodeDecodeError:
            continue
    raise ValueError("Could not decode text file with supported encodings")


def extract_html_text(raw_html: str) -> str:
    parser = TextExtractor()
    parser.feed(raw_html)
    parser.close()
    return html.unescape(parser.text())


def read_html(path: Path) -> tuple[str, str]:
    raw, method = read_text(path)
    return extract_html_text(raw), f"html:{method}"


def strip_rtf(raw: str) -> str:
    raw = re.sub(r"\\'[0-9a-fA-F]{2}", " ", raw)
    raw = re.sub(r"\\par[d]?", "\n", raw)
    raw = re.sub(r"\\tab", "\t", raw)
    raw = re.sub(r"\\[a-zA-Z]+-?\d* ?", "", raw)
    raw = raw.replace("{", " ").replace("}", " ")
    raw = raw.replace("\\", "")
    return normalize_text(raw)


def read_rtf(path: Path) -> tuple[str, str]:
    raw, method = read_text(path)
    return strip_rtf(raw), f"rtf-fallback:{method}"


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_zip_archive(archive: zipfile.ZipFile) -> None:
    entries = [item for item in archive.infolist() if not item.is_dir()]
    if len(entries) > MAX_ARCHIVE_MEMBERS:
        raise ValueError(f"Archive has too many files: {len(entries)} > {MAX_ARCHIVE_MEMBERS}")

    total_size = sum(item.file_size for item in entries)
    if total_size > MAX_ARCHIVE_TOTAL_BYTES:
        raise ValueError(f"Archive uncompressed size is too large: {total_size} > {MAX_ARCHIVE_TOTAL_BYTES} bytes")

    oversized = [item.filename for item in entries if item.file_size > MAX_ARCHIVE_ENTRY_BYTES]
    if oversized:
        raise ValueError(f"Archive entry is too large: {oversized[0]} > {MAX_ARCHIVE_ENTRY_BYTES} bytes")


def text_from_xml(xml_bytes: bytes) -> str:
    root = ElementTree.fromstring(xml_bytes)
    paragraphs: list[str] = []
    current: list[str] = []
    for elem in root.iter():
        tag = elem.tag.rsplit("}", 1)[-1]
        if tag == "t" and elem.text:
            current.append(elem.text)
        elif tag in {"tab"}:
            current.append("\t")
        elif tag in {"br", "cr"}:
            current.append("\n")
        elif tag == "p" and current:
            paragraphs.append("".join(current).strip())
            current = []
    if current:
        paragraphs.append("".join(current).strip())
    return normalize_text("\n\n".join(part for part in paragraphs if part))


def read_docx(path: Path) -> tuple[str, str]:
    parts = ["word/document.xml"]
    with zipfile.ZipFile(path) as archive:
        validate_zip_archive(archive)
        parts.extend(
            name
            for name in archive.namelist()
            if re.match(r"word/(header|footer)\d+\.xml$", name)
        )
        extracted: list[str] = []
        for name in parts:
            if name in archive.namelist():
                extracted.append(text_from_xml(archive.read(name)))
    return normalize_text("\n\n".join(extracted)), "docx-stdlib"


def epub_ordered_items(archive: zipfile.ZipFile) -> list[str]:
    try:
        container = ElementTree.fromstring(archive.read("META-INF/container.xml"))
        rootfile = container.find(".//{*}rootfile")
        if rootfile is None:
            return []
        opf_path = rootfile.attrib["full-path"]
        base = posixpath.dirname(opf_path)
        package = ElementTree.fromstring(archive.read(opf_path))
        manifest = {
            item.attrib["id"]: item.attrib["href"]
            for item in package.findall(".//{*}manifest/{*}item")
            if "id" in item.attrib and "href" in item.attrib
        }
        ordered: list[str] = []
        for itemref in package.findall(".//{*}spine/{*}itemref"):
            href = manifest.get(itemref.attrib.get("idref", ""))
            if href:
                href_path = urllib.parse.unquote(href.split("#", 1)[0])
                ordered.append(posixpath.normpath(posixpath.join(base, href_path)).lstrip("/"))
        return ordered
    except Exception:
        return []


def read_epub(path: Path) -> tuple[str, str]:
    with zipfile.ZipFile(path) as archive:
        validate_zip_archive(archive)
        names = epub_ordered_items(archive)
        if not names:
            names = [
                name
                for name in archive.namelist()
                if name.lower().endswith((".xhtml", ".html", ".htm"))
            ]
        chapters: list[str] = []
        for name in names:
            try:
                raw = archive.read(name).decode("utf-8", errors="replace")
                text = extract_html_text(raw)
                if text:
                    chapters.append(f"# {name}\n\n{text}")
            except KeyError:
                continue
    return normalize_text("\n\n".join(chapters)), "epub-stdlib"


def read_pdf(path: Path) -> tuple[str, str]:
    if not shutil.which("pdftotext"):
        raise ValueError("pdftotext is not installed; cannot extract PDF text")
    try:
        result = subprocess.run(
            ["pdftotext", "-layout", str(path), "-"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        detail = exc.stderr.strip() or str(exc)
        raise ValueError(f"pdftotext failed: {detail}") from exc
    return normalize_text(result.stdout), "pdftotext"


def read_ebook_with_calibre(path: Path, output_dir: Path) -> tuple[str, str]:
    if not shutil.which("ebook-convert"):
        raise ValueError("ebook-convert is not installed; cannot extract this ebook format")
    temp_output = output_dir / f"{path.stem}.txt"
    try:
        subprocess.run(
            ["ebook-convert", str(path), str(temp_output)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        detail = exc.stderr.strip() or str(exc)
        raise ValueError(f"ebook-convert failed: {detail}") from exc
    return read_text(temp_output)[0], "calibre:ebook-convert"


def extract_one(path: Path, output_dir: Path) -> tuple[str, SourceMetadata]:
    extension = path.suffix.lower()
    method = "unknown"
    warning = None
    source_bytes = path.stat().st_size if path.exists() else 0
    sha256: str | None = None
    try:
        if source_bytes > MAX_SOURCE_BYTES:
            raise ValueError(f"Source file is too large: {source_bytes} > {MAX_SOURCE_BYTES} bytes")
        sha256 = file_sha256(path)
        if extension in TEXT_EXTENSIONS:
            text, method = read_text(path)
        elif extension in HTML_EXTENSIONS:
            text, method = read_html(path)
        elif extension in RTF_EXTENSIONS:
            text, method = read_rtf(path)
        elif extension in DOCX_EXTENSIONS:
            text, method = read_docx(path)
        elif extension in EPUB_EXTENSIONS:
            text, method = read_epub(path)
        elif extension in PDF_EXTENSIONS:
            text, method = read_pdf(path)
        elif extension in EBOOK_EXTENSIONS:
            text, method = read_ebook_with_calibre(path, output_dir)
        else:
            raise ValueError(f"Unsupported file extension: {extension}")
        if not text:
            status = "empty"
            warning = "No text extracted"
        else:
            status = "ok"
    except Exception as exc:
        text = ""
        status = "failed"
        warning = str(exc)

    words = len(re.findall(r"\S+", text))
    page_breaks = text.count("<!-- PAGE BREAK -->")
    metadata = SourceMetadata(
        path=str(path),
        resolved_path=str(path.resolve()) if path.exists() else str(path),
        name=path.name,
        format=extension.lstrip("."),
        bytes=source_bytes,
        sha256=sha256,
        characters=len(text),
        words=words,
        estimated_tokens=max(1, int(words * 1.33)) if words else 0,
        page_breaks=page_breaks,
        method=method,
        status=status,
        warning=warning,
    )
    return text, metadata


def resolve_inputs(values: Iterable[str]) -> tuple[list[Path], list[InputWarning]]:
    files: list[Path] = []
    warnings: list[InputWarning] = []
    for value in values:
        matches = sorted(glob.glob(value, recursive=True))
        candidates = matches if matches else [value]
        for candidate in candidates:
            path = Path(candidate).expanduser()
            if path.is_dir():
                before = len(files)
                for child in sorted(path.rglob("*")):
                    if child.is_file() and child.suffix.lower() in SUPPORTED_EXTENSIONS:
                        files.append(child)
                if len(files) == before:
                    warnings.append(InputWarning(str(path), "directory contained no supported files"))
            elif path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
                files.append(path)
            elif path.is_file():
                warnings.append(InputWarning(str(path), f"unsupported extension: {path.suffix.lower() or '(none)'}"))
            else:
                warnings.append(InputWarning(str(path), "path or glob did not match any file or directory"))
    unique: list[Path] = []
    seen: set[Path] = set()
    for path in files:
        resolved = path.resolve()
        if resolved not in seen:
            seen.add(resolved)
            unique.append(path)
    return unique, warnings


def default_output_dir() -> Path:
    configured = os.environ.get("SOURCE_SKILL_WORKDIR")
    if configured:
        return Path(configured)
    return Path(tempfile.mkdtemp(prefix="source_skill_work_"))


def build_run_metadata(argv: list[str] | None = None) -> dict[str, object]:
    metadata: dict[str, object] = {
        "schema_version": METADATA_SCHEMA_VERSION,
        "extractor_version": EXTRACTOR_VERSION,
        "generated_at_utc": datetime.datetime.now(datetime.UTC).replace(microsecond=0).isoformat(),
        "python_version": platform.python_version(),
        "platform": platform.platform(),
    }
    if argv is not None:
        metadata["argv"] = argv
    return metadata


def write_input_list(files: list[Path], input_warnings: list[InputWarning]) -> int:
    payload = {
        **build_run_metadata(),
        "total_sources": len(files),
        "input_warnings": [asdict(item) for item in input_warnings],
        "sources": [
            {
                "path": str(path),
                "resolved_path": str(path.resolve()),
                "name": path.name,
                "format": path.suffix.lower().lstrip("."),
                "bytes": path.stat().st_size,
            }
            for path in files
        ],
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if files else 2


def write_outputs(files: list[Path], output_dir: Path, mode: str, input_warnings: list[InputWarning] | None = None, strict: bool = False, argv: list[str] | None = None) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)
    full_text_path = output_dir / "full_text.md"
    metadata_path = output_dir / "metadata.json"

    sources: list[SourceMetadata] = []
    sections: list[str] = []
    next_line = 1
    for index, path in enumerate(files, start=1):
        text, metadata = extract_one(path, output_dir)
        metadata.source_index = index
        sources.append(metadata)
        warning = metadata.warning or "none"
        section = normalize_text(
            "\n".join(
                [
                    f"<!-- SOURCE {index} START: {path} -->",
                    f"<!-- EXTRACTION status={metadata.status} method={metadata.method} warning={warning} -->",
                    f"# Source {index}: {path.name}",
                    "",
                    text,
                    "",
                    f"<!-- SOURCE {index} END: {path} -->",
                ]
            )
        )
        line_count = len(section.splitlines())
        metadata.full_text_start_line = next_line
        metadata.full_text_end_line = next_line + line_count - 1
        next_line = metadata.full_text_end_line + 2
        sections.append(section)

    full_text = "\n\n".join(sections).strip()
    full_text_path.write_text(full_text + "\n", encoding="utf-8")

    total_words = sum(item.words for item in sources)
    total_tokens = sum(item.estimated_tokens for item in sources)
    metadata = {
        **build_run_metadata(argv),
        "mode": mode,
        "output_dir": str(output_dir),
        "full_text_path": str(full_text_path),
        "total_sources": len(sources),
        "successful_sources": sum(1 for item in sources if item.status == "ok"),
        "failed_sources": sum(1 for item in sources if item.status != "ok"),
        "input_warnings": [asdict(item) for item in input_warnings or []],
        "total_words": total_words,
        "estimated_tokens": total_tokens,
        "sources": [asdict(item) for item in sources],
    }
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Wrote {full_text_path}")
    print(f"Wrote {metadata_path}")
    print(f"Sources: {len(sources)} ok={metadata['successful_sources']} failed={metadata['failed_sources']}")
    if input_warnings:
        print(f"Input warnings: {len(input_warnings)}")
    print(f"Words: {total_words} estimated_tokens={total_tokens}")
    if metadata["successful_sources"] == 0:
        return 1
    if strict and (metadata["failed_sources"] or input_warnings):
        return 1
    return 0


def check_environment() -> int:
    capabilities = {
        "text/markdown/rst/adoc": "stdlib",
        "html/htm": "stdlib HTMLParser",
        "rtf": "stdlib fallback stripper",
        "docx": "stdlib zip+xml",
        "epub": "stdlib zip+xml+HTMLParser",
        "pdf": "pdftotext" if shutil.which("pdftotext") else "missing pdftotext",
        "mobi/azw/azw3": "ebook-convert" if shutil.which("ebook-convert") else "missing ebook-convert",
    }
    print(f"source-to-skill extraction capabilities (extractor {EXTRACTOR_VERSION}, schema {METADATA_SCHEMA_VERSION})")
    for label, capability in capabilities.items():
        print(f"- {label}: {capability}")
    print("\narchive safety limits")
    print(f"- max archive members: {MAX_ARCHIVE_MEMBERS}")
    print(f"- max archive entry bytes: {MAX_ARCHIVE_ENTRY_BYTES}")
    print(f"- max archive total bytes: {MAX_ARCHIVE_TOTAL_BYTES}")
    print(f"- max source file bytes: {MAX_SOURCE_BYTES}")
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract source text for source-to-skill workflows.",
    )
    parser.add_argument("inputs", nargs="*", help="Files, directories, or glob patterns")
    parser.add_argument("--mode", choices=("technical", "text"), default="text")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--strict", action="store_true", help="Exit non-zero if any input is skipped, empty, or failed")
    parser.add_argument("--list", action="store_true", help="List resolved input files and warnings without extracting")
    parser.add_argument("--check", action="store_true", help="Report extraction capabilities")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    raw_argv = sys.argv[1:] if argv is None else argv
    args = parse_args(raw_argv)
    if args.check:
        return check_environment()
    if not args.inputs:
        print("Usage: extract.py <file|directory|glob>... [--mode technical|text] [--output-dir DIR]", file=sys.stderr)
        return 2
    files, input_warnings = resolve_inputs(args.inputs)
    if args.list:
        return write_input_list(files, input_warnings)
    if not files:
        supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        print(f"No supported files found. Supported extensions: {supported}", file=sys.stderr)
        for warning in input_warnings:
            print(f"Input warning: {warning.input}: {warning.reason}", file=sys.stderr)
        return 2
    output_dir = Path(args.output_dir).expanduser() if args.output_dir else default_output_dir()
    return write_outputs(files, output_dir, args.mode, input_warnings, args.strict, raw_argv)


if __name__ == "__main__":
    raise SystemExit(main())