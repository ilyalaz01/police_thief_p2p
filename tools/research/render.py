"""Stable CSV and Markdown analysis rendering for the sensitivity study."""

from __future__ import annotations

import csv
import io
from typing import Any


def summary_csv(summary: list[dict[str, Any]]) -> bytes:
    """Serialize the aggregate rows as deterministic UTF-8 CSV."""
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=list(summary[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(summary)
    return stream.getvalue().encode("utf-8")


def analysis_markdown(
    summary: list[dict[str, Any]], effects: list[dict[str, Any]], design: dict[str, Any]
) -> bytes:
    """Render a notebook-equivalent analysis with equations, tables, and limitations."""
    lines = [
        "# Policy Sensitivity Analysis — Reproducible Notebook Equivalent", "",
        "> Local simulator experiment only. This is not interoperability, public transport,",
        "> an uncounted warm-up, or a counted league operation.", "",
        "## Question and preregistered design", "",
        design["research_question"], "",
        f"The run uses {design['expected_games']:,} games: 40 paired seeds, three start scenarios,",
        "four existing policy pairings, and five one-factor-at-a-time (OAT) settings. All other",
        "GameConfig fields remain fixed. ScentTacticalPolice remains frozen; no policy was trained",
        "or changed.", "",
        "## Estimands and equations", "",
        "Capture rate is $\\hat{p}=c/n$. Uncertainty uses the Wilson 95% score interval:", "",
        "$$\\frac{\\hat p + z^2/(2n) \\pm "
        "z\\sqrt{\\hat p(1-\\hat p)/n+z^2/(4n^2)}}"
        "{1+z^2/n},\\quad z=1.95996.$$", "",
        "The paired OAT elementary effect for factor $i$ is", "",
        "$$\\Delta_i = \\frac{\\hat p(x_i')-\\hat p(x_i)}{x_i'-x_i}.$$",
        "",
        "## Aggregate results", "",
        "| Setting | Police | Thief | Games | Capture | Wilson 95% | Police score | Thief score |",
        "|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in summary:
        lines.append(
            f"| {row['setting']} | {row['police_policy']} | {row['thief_policy']} | "
            f"{row['games']} | {row['capture_rate']:.1%} | "
            f"[{row['wilson_95_low']:.1%}, {row['wilson_95_high']:.1%}] | "
            f"{row['mean_police_score']:.2f} | {row['mean_thief_score']:.2f} |"
        )
    lines.extend(["", "## Paired elementary effects", "",
        "| Setting | Pairing | Capture delta | Effect per unit |",
        "|---|---|---:|---:|"])
    for row in effects:
        pairing = f"{row['police_policy']} vs {row['thief_policy']}"
        lines.append(
            f"| {row['setting']} | {pairing} | "
            f"{row['paired_capture_delta_from_baseline']:+.1%} | "
            f"{row['elementary_effect_per_parameter_unit']:+.5f} |"
        )
    lines.extend(_interpretation(summary, effects))
    return ("\n".join(lines) + "\n").encode("utf-8")


def _interpretation(
    summary: list[dict[str, Any]], effects: list[dict[str, Any]]
) -> list[str]:
    """Return bounded interpretation, threats to validity, and primary citations."""
    champion = [row for row in summary if row["police_policy"] == "ScentTacticalPolice"]
    baseline = [row for row in champion if row["setting"] == "board_7_survival_35"]
    largest = max(effects, key=lambda row: abs(row["paired_capture_delta_from_baseline"]))
    return ["", "## Interpretation", "",
        f"The frozen champion baseline spans {min(r['capture_rate'] for r in baseline):.1%} to "
        f"{max(r['capture_rate'] for r in baseline):.1%} across the two Thief policies "
        "after pooling scenarios.",
        "The largest observed paired shift is "
        f"{largest['paired_capture_delta_from_baseline']:+.1%} "
        f"for {largest['police_policy']} vs {largest['thief_policy']} at {largest['setting']}.",
        "These are measured associations inside the declared simulator grid, not a new competitive",
        "policy decision and not evidence about another team's implementation.", "",
        "## Limitations and threats to validity", "",
        "- OAT is a screening design and cannot estimate factor interactions; this is not a Sobol",
        "  or other global variance-based sensitivity analysis.",
        "- Forty deterministic seeds and three starts support paired comparison but do not",
        "  make the",
        "  confidence interval a guarantee for unseen terrains, teams, or implementations.",
        "- The simulator exposes evaluator outcomes only after actions; policies still receive",
        "  Observation-only inputs. No objective opponent coordinate is published.",
        "- Timing is deliberately excluded from deterministic artifacts and remains under",
        "  COST-001.", "",
        "## References", "",
        "- Morris (1991), OAT elementary effects: https://doi.org/10.1080/00401706.1991.10484804",
        "- Saltelli et al. (2010), variance-based global sensitivity and interaction limits:",
        "  https://doi.org/10.1016/j.cpc.2009.09.018",
        "- Wilson (1927), binomial score interval:",
        "  https://doi.org/10.1080/01621459.1927.10502953", "",
        "## Reproduction", "",
        "```bash", "uv run python -m tools.research.cli", "```", "",
        "The command performs only local simulator experiments and overwrites only the six curated",
        "publication files listed in the manifest."]
