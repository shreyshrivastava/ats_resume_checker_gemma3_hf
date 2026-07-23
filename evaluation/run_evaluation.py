from __future__ import annotations

import argparse
import json
import platform
import sys
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.scorer import analyze_resume  # noqa: E402

DATASET_PATH = ROOT / "evaluation" / "datasets" / "resume_job_pairs.json"
RESULTS_JSON = ROOT / "evaluation" / "results.json"
RESULTS_MD = ROOT / "evaluation" / "results.md"


def load_cases(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate_cases(cases: list[dict]) -> dict:
    evaluated = []
    groups: dict[str, list[dict]] = defaultdict(list)

    for case in cases:
        analysis = analyze_resume(case["resume_text"], case["job_description"])
        row = {
            "id": case["id"],
            "group": case["group"],
            "expected_strength": case["expected_strength"],
            "score": analysis["score"],
            "verdict": analysis["verdict"],
            "matched_terms": analysis["matched_terms"],
            "missing_terms": analysis["missing_terms"],
        }
        evaluated.append(row)
        groups[case["group"]].append(row)

    group_results = []
    for group, rows in groups.items():
        expected = sorted(rows, key=lambda row: row["expected_strength"], reverse=True)
        actual = sorted(rows, key=lambda row: row["score"], reverse=True)
        group_results.append(
            {
                "group": group,
                "expected_order": [row["id"] for row in expected],
                "actual_order": [row["id"] for row in actual],
                "ranking_consistent": [row["id"] for row in expected]
                == [row["id"] for row in actual],
            }
        )

    passed_groups = sum(1 for group in group_results if group["ranking_consistent"])
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
        },
        "case_count": len(evaluated),
        "ranking_groups": len(group_results),
        "ranking_consistency_rate": passed_groups / max(1, len(group_results)),
        "cases": evaluated,
        "groups": group_results,
    }


def write_markdown(results: dict, path: Path) -> None:
    lines = [
        "# Evaluation Results",
        "",
        "Synthetic, anonymized resume/job-description pairs are used to check deterministic ranking behavior.",
        "",
        f"- Generated at: `{results['generated_at']}`",
        f"- Cases: `{results['case_count']}`",
        f"- Ranking groups: `{results['ranking_groups']}`",
        f"- Ranking consistency rate: `{results['ranking_consistency_rate']:.2%}`",
        "",
        "## Ranking Groups",
        "",
    ]
    for group in results["groups"]:
        status = "pass" if group["ranking_consistent"] else "fail"
        lines.extend(
            [
                f"### {group['group']} ({status})",
                "",
                f"- Expected: `{', '.join(group['expected_order'])}`",
                f"- Actual: `{', '.join(group['actual_order'])}`",
                "",
            ]
        )

    lines.extend(["## Case Scores", ""])
    for case in results["cases"]:
        lines.append(
            f"- `{case['id']}`: score `{case['score']}`, verdict `{case['verdict']}`"
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run deterministic ATS ranking evaluation.")
    parser.add_argument("--dataset", type=Path, default=DATASET_PATH)
    parser.add_argument("--results-json", type=Path, default=RESULTS_JSON)
    parser.add_argument("--results-md", type=Path, default=RESULTS_MD)
    args = parser.parse_args()

    cases = load_cases(args.dataset)
    results = evaluate_cases(cases)
    args.results_json.write_text(json.dumps(results, indent=2), encoding="utf-8")
    write_markdown(results, args.results_md)

    if results["ranking_consistency_rate"] < 1:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
