"""Parse MaByte Code Assistant markdown output into downloadable files."""
from __future__ import annotations

import io
import re
import zipfile
from dataclasses import dataclass

CODE_BLOCK_RE = re.compile(r"```([^\n`]*)\n(.*?)```", re.DOTALL)

FILE_HINT_PATTERNS = (
    re.compile(r"<!--\s*file(?:name)?:\s*([^\s>]+)\s*-->", re.I),
    re.compile(r"/\*\s*file(?:name)?:\s*([^\s*]+)\s*\*/", re.I),
    re.compile(r"//\s*file(?:name)?:\s*(\S+)", re.I),
    re.compile(r"#\s*file(?:name)?:\s*(\S+)", re.I),
)

LANG_TO_EXT: dict[str, str] = {
    "html": "html",
    "htm": "html",
    "css": "css",
    "javascript": "js",
    "js": "js",
    "typescript": "ts",
    "ts": "ts",
    "tsx": "tsx",
    "jsx": "jsx",
    "python": "py",
    "py": "py",
    "json": "json",
    "sql": "sql",
    "yaml": "yaml",
    "yml": "yml",
    "xml": "xml",
    "bash": "sh",
    "sh": "sh",
    "shell": "sh",
    "php": "php",
    "java": "java",
    "go": "go",
    "rust": "rs",
    "c": "c",
    "cpp": "cpp",
    "csharp": "cs",
    "cs": "cs",
}

DEFAULT_FILENAMES: dict[str, str] = {
    "html": "index.html",
    "css": "styles.css",
    "js": "app.js",
    "ts": "app.ts",
    "tsx": "App.tsx",
    "jsx": "App.jsx",
    "py": "main.py",
    "json": "data.json",
    "sql": "query.sql",
}

EXT_MIME: dict[str, str] = {
    "html": "text/html",
    "css": "text/css",
    "js": "application/javascript",
    "ts": "application/typescript",
    "tsx": "text/plain",
    "jsx": "text/plain",
    "py": "text/x-python",
    "json": "application/json",
    "sql": "application/sql",
    "xml": "application/xml",
    "yaml": "text/yaml",
    "yml": "text/yaml",
    "sh": "application/x-sh",
    "php": "application/x-httpd-php",
}


@dataclass(frozen=True)
class CodeFile:
    filename: str
    content: str
    language: str
    extension: str

    @property
    def mime(self) -> str:
        return EXT_MIME.get(self.extension, "text/plain")


def _parse_fence_tag(tag: str) -> tuple[str, str | None]:
    tag = (tag or "").strip()
    if not tag:
        return "", None
    if "." in tag and " " not in tag and "/" not in tag:
        return "", tag
    parts = tag.split(None, 1)
    lang = parts[0].lower()
    filename = parts[1].strip() if len(parts) > 1 else None
    return lang, filename


def _hint_filename(content: str) -> str | None:
    for line in content.split("\n", 3)[:3]:
        for pattern in FILE_HINT_PATTERNS:
            match = pattern.search(line)
            if match:
                return match.group(1).strip()
    return None


def _strip_file_hint(content: str) -> str:
    lines = content.split("\n", 1)
    if not lines:
        return content
    if any(pattern.search(lines[0]) for pattern in FILE_HINT_PATTERNS):
        return lines[1].lstrip("\n") if len(lines) > 1 else ""
    return content


def _sniff_language(content: str) -> str:
    head = content.lstrip()[:800].lower()
    if "<!doctype html" in head or "<html" in head:
        return "html"
    if re.search(r"^\s*[\w.#\[\]:,]+\s*\{", content, re.M):
        return "css"
    if re.search(r"\b(function|const|let|var|document\.|window\.)\b", content):
        return "js"
    if re.search(r"^\s*def\s+\w+\(", content, re.M):
        return "py"
    return ""


def _extension_for_language(lang: str) -> str:
    return LANG_TO_EXT.get(lang.lower(), lang.lower() if lang else "txt")


def _default_filename(lang: str) -> str:
    ext = _extension_for_language(lang)
    return DEFAULT_FILENAMES.get(ext, f"code.{ext}" if ext else "code.txt")


def _unique_filename(name: str, seen: set[str]) -> str:
    if name not in seen:
        seen.add(name)
        return name
    stem, dot, ext = name.rpartition(".")
    if not dot:
        stem, ext = name, ""
    index = 2
    while True:
        candidate = f"{stem}_{index}.{ext}" if ext else f"{stem}_{index}"
        if candidate not in seen:
            seen.add(candidate)
            return candidate
        index += 1


def _resolve_filename(lang: str, fence_name: str | None, hint: str | None) -> str:
    for candidate in (hint, fence_name):
        if candidate and "." in candidate:
            return candidate.split("/")[-1].split("\\")[-1]
    return _default_filename(lang)


def parse_code_output(text: str) -> list[CodeFile]:
    """Extract code files from markdown assistant output."""
    seen: set[str] = set()
    files: list[CodeFile] = []

    for match in CODE_BLOCK_RE.finditer(text):
        raw_content = match.group(2).rstrip("\n")
        if not raw_content.strip():
            continue

        lang, fence_name = _parse_fence_tag(match.group(1))
        hint = _hint_filename(raw_content)
        content = _strip_file_hint(raw_content)

        if not lang:
            lang = _sniff_language(content)

        filename = _resolve_filename(lang, fence_name, hint)
        filename = _unique_filename(filename, seen)
        ext = filename.rpartition(".")[2].lower() or _extension_for_language(lang)

        files.append(
            CodeFile(
                filename=filename,
                content=content,
                language=lang or ext,
                extension=ext,
            )
        )

    return files


def build_zip(files: list[CodeFile]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for item in files:
            archive.writestr(item.filename, item.content.encode("utf-8"))
    return buffer.getvalue()


def prose_without_code_blocks(text: str) -> str:
    return CODE_BLOCK_RE.sub("", text).strip()


def download_label_for_file(item: CodeFile) -> str:
    labels = {
        "html": "Herunterladen als HTML",
        "css": "Herunterladen als CSS",
        "js": "Herunterladen als JavaScript",
        "py": "Herunterladen als Python",
        "json": "Herunterladen als JSON",
        "ts": "Herunterladen als TypeScript",
    }
    return labels.get(item.extension, f"Herunterladen ({item.filename})")
