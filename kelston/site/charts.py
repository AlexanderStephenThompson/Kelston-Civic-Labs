"""Inline SVG chart primitives - pure functions, no dependencies, every
label a visible <text> element. The portal's charts are generated
server-side from the same fixtures the validator proves."""

from __future__ import annotations

import re
from html import escape

ACCENT = "#166e5a"
PALETTE = ["#166e5a", "#559682", "#8cbcab", "#c3ddd3", "#8b9491", "#5c6663", "#343b39"]


def _title_id(title: str) -> str:
    return "chart-" + re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")


def horizontal_bar(
    rows: list[tuple[str, float]],
    *,
    title: str,
    value_format: str = "{:,.0f}",
    unit: str = "",
    color: str = ACCENT,
) -> str:
    label_w, bar_w, row_h, pad = 190, 360, 28, 8
    width = label_w + bar_w + 96
    height = pad * 2 + max(len(rows), 1) * row_h
    peak = max((value for _, value in rows), default=1) or 1
    tid = _title_id(title)
    suffix = f" ({unit})" if unit else ""
    parts = [
        f'<svg viewBox="0 0 {width} {height}" role="img" aria-labelledby="{tid}" class="chart">',
        f'<title id="{tid}">{escape(title)}{escape(suffix)}</title>',
    ]
    for index, (label, value) in enumerate(rows):
        y = pad + index * row_h
        bar = round(bar_w * value / peak, 1)
        parts.append(
            f'<text x="{label_w - 8}" y="{y + 17}" text-anchor="end" class="c-label">'
            f"{escape(str(label))}</text>"
        )
        parts.append(
            f'<rect x="{label_w}" y="{y + 5}" width="{bar}" height="16" fill="{color}" rx="1"/>'
        )
        parts.append(
            f'<text x="{label_w + bar + 6}" y="{y + 17}" class="c-value">'
            f"{value_format.format(value)}</text>"
        )
    parts.append("</svg>")
    return "".join(parts)


def stacked_bar(
    rows: list[tuple[str, dict[str, float]]],
    series: list[str],
    *,
    title: str,
    palette: list[str] | None = None,
) -> str:
    palette = palette or PALETTE
    label_w, bar_w, row_h, pad, legend_h = 190, 360, 28, 8, 26
    width = label_w + bar_w + 96
    height = pad * 2 + legend_h + max(len(rows), 1) * row_h
    peak = max((sum(values.values()) for _, values in rows), default=1) or 1
    tid = _title_id(title)
    parts = [
        f'<svg viewBox="0 0 {width} {height}" role="img" aria-labelledby="{tid}" class="chart">',
        f'<title id="{tid}">{escape(title)}</title>',
    ]
    x = label_w
    for index, name in enumerate(series):
        color = palette[index % len(palette)]
        parts.append(f'<rect x="{x}" y="{pad}" width="12" height="12" fill="{color}" rx="1"/>')
        parts.append(
            f'<text x="{x + 17}" y="{pad + 11}" class="c-label">{escape(name)}</text>'
        )
        x += 24 + 8 * len(name) + 16
    for index, (label, values) in enumerate(rows):
        y = pad + legend_h + index * row_h
        total = sum(values.values())
        parts.append(
            f'<text x="{label_w - 8}" y="{y + 17}" text-anchor="end" class="c-label">'
            f"{escape(str(label))}</text>"
        )
        cursor = float(label_w)
        for series_index, name in enumerate(series):
            value = values.get(name, 0)
            if value <= 0:
                continue
            segment = bar_w * value / peak
            color = palette[series_index % len(palette)]
            parts.append(
                f'<rect x="{round(cursor, 1)}" y="{y + 5}" width="{round(segment, 1)}" '
                f'height="16" fill="{color}"/>'
            )
            cursor += segment
        parts.append(
            f'<text x="{round(cursor, 1) + 6}" y="{y + 17}" class="c-value">{total:,.0f}</text>'
        )
    parts.append("</svg>")
    return "".join(parts)


def donut(
    parts_data: list[tuple[str, float]],
    *,
    title: str,
    palette: list[str] | None = None,
) -> str:
    palette = palette or PALETTE
    size, radius, hole = 168, 60, 38
    legend_x = size + 12
    rows = [(label, value) for label, value in parts_data if value > 0]
    total = sum(value for _, value in rows) or 1
    height = max(size, 18 + len(rows) * 22)
    width = legend_x + 280
    circumference = 2 * 3.141592653589793 * radius
    tid = _title_id(title)
    parts = [
        f'<svg viewBox="0 0 {width} {height}" role="img" aria-labelledby="{tid}" class="chart">',
        f'<title id="{tid}">{escape(title)}</title>',
        f'<circle cx="{size // 2}" cy="{size // 2}" r="{radius}" fill="none" '
        f'stroke="#e2e6e4" stroke-width="{radius - hole}"/>',
    ]
    offset = circumference * 0.25  # start at 12 o'clock
    for index, (label, value) in enumerate(rows):
        share = value / total
        dash = round(circumference * share, 2)
        color = palette[index % len(palette)]
        parts.append(
            f'<circle cx="{size // 2}" cy="{size // 2}" r="{radius}" fill="none" '
            f'stroke="{color}" stroke-width="{radius - hole}" '
            f'stroke-dasharray="{dash} {round(circumference - dash, 2)}" '
            f'stroke-dashoffset="{round(offset, 2)}"/>'
        )
        offset -= dash
        y = 18 + index * 22
        parts.append(f'<rect x="{legend_x}" y="{y - 10}" width="12" height="12" '
                     f'fill="{color}" rx="1"/>')
        parts.append(
            f'<text x="{legend_x + 18}" y="{y + 1}" class="c-label">'
            f"{escape(str(label))} - {value:,.0f} ({share:.0%})</text>"
        )
    parts.append("</svg>")
    return "".join(parts)
