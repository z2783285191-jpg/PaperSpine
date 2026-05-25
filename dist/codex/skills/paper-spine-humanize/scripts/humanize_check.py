#!/usr/bin/env python3
"""Validate PaperSpine humanize_matrix.md — check coverage, scan residual AI patterns."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

from _paper_spine_utils import markdown_tables, read_text, split_paragraphs

CNKI_DIMENSIONS = {
    "sentence structure",
    "paragraph similarity",
    "information density",
    "connector frequency",
    "term-context matching",
}

HIGH_RISK_CONNECTORS_ZH = [
    "首先", "其次", "再次", "最后", "综上所述", "总而言之", "总的来说",
    "此外", "另外", "不仅如此", "值得注意的是", "需要指出的是", "不容忽视的是",
    "具有重要意义", "为……奠定基础", "在……的过程中", "不仅……而且",
]
HIGH_RISK_CONNECTORS_EN = [
    "firstly", "secondly", "thirdly", "finally", "in conclusion", "to sum up",
    "furthermore", "moreover", "additionally", "it is worth noting",
    "it should be pointed out", "it cannot be ignored",
]


@dataclass
class HumanizeCheckResult:
    path: str
    ok: bool
    findings: list[str] = field(default_factory=list)
    matrix_rows: int = 0
    manuscript_paragraphs: int = 0
    residual_connectors: int = 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate PaperSpine humanize_matrix.md.")
    parser.add_argument("output_dir", nargs="?", default="paper_rewriting_output")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--markdown", action="store_true")
    parser.add_argument("--write", action="store_true")
    return parser.parse_args()


def count_connectors(text: str, lang: str) -> int:
    patterns = HIGH_RISK_CONNECTORS_ZH if lang == "zh" else HIGH_RISK_CONNECTORS_EN
    return sum(len(re.findall(re.escape(p), text, re.IGNORECASE)) for p in patterns)


def load_config(out_dir: Path) -> dict:
    config_path = out_dir / "paper_spine_config.json"
    if config_path.exists():
        return json.loads(config_path.read_text(encoding="utf-8"))
    return {}


def check(out_dir: Path) -> HumanizeCheckResult:
    config = load_config(out_dir)
    lang = config.get("output_language", "en")
    findings: list[str] = []

    matrix_path = out_dir / "humanize_matrix.md"
    if not matrix_path.exists():
        return HumanizeCheckResult(str(matrix_path), False, ["humanize_matrix.md not found"])

    matrix_text = matrix_path.read_text(encoding="utf-8", errors="ignore")
    tables = markdown_tables(matrix_text)
    if not tables:
        findings.append("No parseable table in humanize_matrix.md")

    matrix_rows = len(tables[0]) - 1 if tables else 0

    # Check required columns
    if tables:
        header = " ".join(c.lower() for c in tables[0][0])
        for required in ("ai pattern", "detection dimension", "applied change", "teaching"):
            if required not in header:
                findings.append(f"Missing column: {required}")

    # Count manuscript paragraphs
    final_paper = out_dir / "final_paper"
    manuscript_paragraphs = 0
    if final_paper.is_dir():
        for tex_file in final_paper.glob("*.tex"):
            text = tex_file.read_text(encoding="utf-8", errors="ignore")
            manuscript_paragraphs += len(split_paragraphs(text))

    # Check coverage: matrix should cover most paragraphs
    if manuscript_paragraphs > 0 and matrix_rows < manuscript_paragraphs * 0.5:
        findings.append(f"Low coverage: {matrix_rows} matrix rows for ~{manuscript_paragraphs} manuscript paragraphs")

    # Check severity distribution
    if tables:
        severity_count = {"high": 0, "medium": 0, "low": 0}
        for row in tables[0][1:]:
            joined = " ".join(row).lower()
            if "high" in joined:
                severity_count["high"] += 1
            elif "medium" in joined:
                severity_count["medium"] += 1
            elif "low" in joined:
                severity_count["low"] += 1
        if severity_count["high"] == 0 and matrix_rows > 2:
            findings.append("No high-severity patterns found — matrix may be under-reporting")

    # Check dimension coverage
    if tables:
        dimension_hits = set()
        for row in tables[0][1:]:
            joined = " ".join(row).lower()
            for dim in CNKI_DIMENSIONS:
                if dim in joined:
                    dimension_hits.add(dim)
        missing_dims = CNKI_DIMENSIONS - dimension_hits
        if missing_dims:
            findings.append(f"Dimensions not covered: {', '.join(sorted(missing_dims))}")

    # Scan manuscript for residual AI connectors
    residual = 0
    if final_paper.is_dir():
        for tex_file in final_paper.glob("*.tex"):
            text = tex_file.read_text(encoding="utf-8", errors="ignore")
            residual += count_connectors(text, lang)

    if residual > 0 and lang == "zh":
        para_count = max(1, manuscript_paragraphs)
        if residual / para_count > 1.0:
            findings.append(f"High residual connector density: {residual} connectors in {manuscript_paragraphs} paragraphs ({residual / para_count:.1f}/paragraph)")

    return HumanizeCheckResult(
        str(matrix_path),
        not findings,
        findings,
        matrix_rows,
        manuscript_paragraphs,
        residual,
    )


def to_markdown(result: HumanizeCheckResult) -> str:
    lines = [
        "# Humanize Check Report",
        "",
        f"- Matrix path: `{result.path}`",
        f"- Matrix rows: {result.matrix_rows}",
        f"- Manuscript paragraphs: {result.manuscript_paragraphs}",
        f"- Residual AI connectors: {result.residual_connectors}",
        f"- Status: {'PASS' if result.ok else 'FAIL'}",
        "",
        "## Findings",
        "",
    ]
    lines.extend(f"- {f}" for f in result.findings) if result.findings else lines.append("- None")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    out_dir = Path(args.output_dir)
    result = check(out_dir)

    if args.json:
        print(json.dumps({
            "ok": result.ok, "matrix_rows": result.matrix_rows,
            "manuscript_paragraphs": result.manuscript_paragraphs,
            "residual_connectors": result.residual_connectors,
            "findings": result.findings,
        }, ensure_ascii=False, indent=2))
    if args.markdown or not args.json:
        print(to_markdown(result))

    if args.write:
        report_path = out_dir / "humanize_report.md"
        report_path.write_text(to_markdown(result), encoding="utf-8")
        print(f"Wrote {report_path}", file=sys.stderr)

    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
