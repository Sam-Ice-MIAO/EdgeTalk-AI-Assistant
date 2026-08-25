import json
import sys
from pathlib import Path


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


from src.report.poc_report import (
    save_poc_report,
)


EVALUATION_PATH = (
    PROJECT_ROOT
    / "eval"
    / "results"
    / "latest.json"
)

REPORT_PATH = (
    PROJECT_ROOT
    / "reports"
    / "latest_poc_report.md"
)


def main():
    if not EVALUATION_PATH.exists():
        raise FileNotFoundError(
            "Evaluation result not found. "
            "Run python eval/run_eval.py first."
        )

    with open(
        EVALUATION_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        evaluation_data = json.load(
            file
        )

    path = save_poc_report(
        evaluation_data,
        REPORT_PATH,
    )

    summary = evaluation_data.get(
        "summary",
        {},
    )

    print()
    print(
        "EdgeTalk Pro PoC Report"
    )

    print(
        "=" * 50
    )

    print(
        f"Report generated: {path}"
    )

    print(
        "Pass Rate:",
        f"{summary.get('pass_rate', 0)}%",
    )

    print(
        "Acceptance:",
        (
            "PASS"
            if summary.get(
                "accepted",
                False,
            )
            else "FAIL"
        ),
    )


if __name__ == "__main__":
    main()
