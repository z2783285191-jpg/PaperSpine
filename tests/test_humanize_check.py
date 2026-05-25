"""Tests for humanize_check.py."""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "scripts"))
from humanize_check import check, count_connectors, HumanizeCheckResult, to_markdown


class HumanizeCheckTests(unittest.TestCase):
    def _make_out_dir(self, **files: str) -> Path:
        tmp = Path(tempfile.mkdtemp())
        (tmp / "paper_spine_config.json").write_text('{"output_language": "zh"}', encoding="utf-8")
        (tmp / "final_paper").mkdir()
        for name, content in files.items():
            (tmp / name).parent.mkdir(parents=True, exist_ok=True)
            (tmp / name).write_text(content, encoding="utf-8")
        return tmp

    def test_missing_matrix(self) -> None:
        out = self._make_out_dir()
        result = check(out)
        self.assertFalse(result.ok)
        self.assertIn("not found", result.findings[0])

    def test_low_coverage(self) -> None:
        out = self._make_out_dir(**{
            "humanize_matrix.md": (
                "| Row ID | Manuscript Unit | AI Pattern Found | Detection Dimension | Severity | Applied Change | Expected Effect | Teaching Note |\n"
                "|---|---|---|---|---|---|---|---|\n"
                "| 1 | P1 | uniform length | sentence structure | High | varied | lower | why |\n"
            ),
            "final_paper/main.tex": "段落一。" + "x " * 50 + "\n\n段落二。" + "y " * 50 + "\n\n段落三。" + "z " * 50,
        })
        result = check(out)
        self.assertTrue(any("coverage" in f for f in result.findings))

    def test_missing_dimensions(self) -> None:
        out = self._make_out_dir(**{
            "humanize_matrix.md": (
                "| Row ID | Unit | AI Pattern Found | Detection Dimension | Severity | Applied Change | Expected Effect | Teaching Note |\n"
                "|---|---|---|---|---|---|---|---|\n"
                "| 1 | P1 | uniform | sentence structure | High | varied | lower | why |\n"
            ),
        })
        result = check(out)
        self.assertTrue(any("not covered" in f for f in result.findings))

    def test_count_connectors_zh(self) -> None:
        cnt = count_connectors("首先，这是一个问题。此外，还有另一个方面。综上所述，结论成立。", "zh")
        self.assertEqual(cnt, 3)

    def test_to_markdown(self) -> None:
        result = HumanizeCheckResult("test.md", True, [], 5, 10, 2)
        md = to_markdown(result)
        self.assertIn("PASS", md)

    def test_json_output(self) -> None:
        import json
        result = HumanizeCheckResult("test.md", False, ["gap"], 3, 8, 5)
        output = json.dumps({"ok": result.ok, "findings": result.findings})
        data = json.loads(output)
        self.assertFalse(data["ok"])


if __name__ == "__main__":
    unittest.main()
