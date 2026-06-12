"""Rendering machinery: the Jinja environment, the page write loop, the
relative-root scheme that keeps every link sub-path safe, and a tiny
markdown-to-HTML converter for changelog files."""

from __future__ import annotations

from dataclasses import dataclass, field
from html import escape
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

TEMPLATES_DIR = Path(__file__).parent / "templates"
STATIC_DIR = Path(__file__).parent / "static"


def environment() -> Environment:
    return Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=select_autoescape(["html"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )


@dataclass
class Page:
    rel_path: str  # e.g. "realms/commons/index.html"
    template: str
    context: dict = field(default_factory=dict)

    @property
    def root(self) -> str:
        depth = self.rel_path.count("/")
        return "../" * depth


def write_pages(pages: list[Page], output: Path, shared: dict) -> int:
    env = environment()
    for page in pages:
        template = env.get_template(page.template)
        html = template.render({**shared, **page.context, "root": page.root})
        target = output / page.rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(html, encoding="utf-8")
    return len(pages)


def copy_static(output: Path) -> None:
    target = output / "static"
    target.mkdir(parents=True, exist_ok=True)
    for source in STATIC_DIR.iterdir():
        (target / source.name).write_bytes(source.read_bytes())


def markdown_to_html(text: str) -> str:
    """Just enough markdown for the registry changelogs: headings, bullets,
    inline code, paragraphs."""
    lines = text.splitlines()
    out: list[str] = []
    in_list = False
    for raw in lines:
        line = raw.rstrip()
        if line.startswith("#"):
            if in_list:
                out.append("</ul>")
                in_list = False
            level = min(len(line) - len(line.lstrip("#")), 4)
            out.append(f"<h{level + 1}>{_inline(line.lstrip('# '))}</h{level + 1}>")
        elif line.startswith("- "):
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{_inline(line[2:])}</li>")
        elif line.strip() == "":
            if in_list:
                out.append("</ul>")
                in_list = False
        else:
            out.append(f"<p>{_inline(line)}</p>")
    if in_list:
        out.append("</ul>")
    return "\n".join(out)


def _inline(text: str) -> str:
    escaped = escape(text)
    parts = escaped.split("`")
    for index in range(1, len(parts), 2):
        parts[index] = f"<code>{parts[index]}</code>"
    return "".join(parts)
