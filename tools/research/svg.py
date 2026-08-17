"""Accessible dependency-free SVG line-chart rendering."""

from __future__ import annotations

import html
from typing import Any

COLORS = ("#0072B2", "#D55E00", "#009E73", "#CC79A7")


def render_chart(
    summary: list[dict[str, Any]], factor: str, values: tuple[int, ...], title: str
) -> bytes:
    """Render capture rates and Wilson intervals for one OAT factor."""
    rows = [row for row in summary if _belongs(row, factor)]
    pairings = list(dict.fromkeys((row["police_policy"], row["thief_policy"]) for row in rows))
    x_positions = {value: 150 + index * 390 for index, value in enumerate(values)}
    lines = [_header(title, factor), _axes(values, x_positions, factor)]
    for index, pairing in enumerate(pairings):
        color = COLORS[index]
        points = sorted(
            (_x_value(row, factor), row) for row in rows
            if (row["police_policy"], row["thief_policy"]) == pairing
        )
        path = " ".join(
            f"{'M' if offset == 0 else 'L'} {x_positions[value]} {_y(row['capture_rate'])}"
            for offset, (value, row) in enumerate(points)
        )
        lines.append(f'<path d="{path}" fill="none" stroke="{color}" stroke-width="4"/>')
        for value, row in points:
            x, y = x_positions[value], _y(row["capture_rate"])
            low, high = _y(row["wilson_95_low"]), _y(row["wilson_95_high"])
            lines.append(f'<line x1="{x}" y1="{high}" x2="{x}" y2="{low}" stroke="{color}"/>')
            lines.append(f'<circle cx="{x}" cy="{y}" r="7" fill="{color}"/>')
        label = html.escape(f"{pairing[0]} vs {pairing[1]}")
        legend_y = 525 + index * 34
        lines.append(
            f'<line x1="730" y1="{legend_y}" x2="775" y2="{legend_y}" '
            f'stroke="{color}" stroke-width="4"/>'
        )
        lines.append(f'<text x="790" y="{legend_y + 6}" class="legend">{label}</text>')
    lines.append("</svg>\n")
    return "\n".join(lines).encode("utf-8")


def _header(title: str, factor: str) -> str:
    """Return SVG metadata, accessible description, and shared styles."""
    escaped = html.escape(title)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="700"
viewBox="0 0 1200 700" role="img">
<title>{escaped}</title>
<desc>Capture rate by {html.escape(factor)}. Lines compare four existing policy pairings;
vertical marks are Wilson 95 percent intervals.</desc>
<style>text{{font-family:Arial,sans-serif;fill:#222}}.axis{{font-size:20px}}
.legend{{font-size:16px}}.title{{font-size:28px;font-weight:bold}}</style>
<rect width="1200" height="700" fill="#FFFFFF"/>
<text x="600" y="42" text-anchor="middle" class="title">{escaped}</text>'''


def _axes(values: tuple[int, ...], positions: dict[int, int], factor: str) -> str:
    """Render labelled axes and horizontal percentage grid lines."""
    parts = ['<line x1="100" y1="80" x2="100" y2="480" stroke="#222" stroke-width="2"/>']
    parts.append('<line x1="100" y1="480" x2="1000" y2="480" stroke="#222" stroke-width="2"/>')
    for tick in range(0, 101, 20):
        y = _y(tick / 100)
        parts.append(f'<line x1="100" y1="{y}" x2="1000" y2="{y}" stroke="#D9D9D9"/>')
        parts.append(f'<text x="88" y="{y + 6}" text-anchor="end" class="axis">{tick}%</text>')
    for value in values:
        parts.append(
            f'<text x="{positions[value]}" y="510" text-anchor="middle" '
            f'class="axis">{value}</text>'
        )
    parts.append(
        '<text x="550" y="550" text-anchor="middle" class="axis">'
        f"{html.escape(factor)}</text>"
    )
    return "\n".join(parts)


def _belongs(row: dict[str, Any], factor: str) -> bool:
    """Select the baseline plus settings that vary only the requested factor."""
    return row["factor"] in {"baseline", factor}


def _x_value(row: dict[str, Any], factor: str) -> int:
    """Return the plotted parameter value, including the shared baseline."""
    return row[factor]


def _y(rate: float) -> float:
    """Map a capture proportion onto the fixed vertical plot area."""
    return round(480 - rate * 400, 3)
