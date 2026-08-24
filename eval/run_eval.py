import json
import time
import urllib.error
import urllib.request

from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

TEST_CASES_PATH = (
    PROJECT_ROOT
    / "eval"
    / "test_cases.json"
)

RESULTS_DIR = (
    PROJECT_ROOT
    / "eval"
    / "results"
)

LATEST_RESULT_PATH = (
    RESULTS_DIR
    / "latest.json"
)

API_URL = (
    "http://127.0.0.1:8000/agent-chat"
)


CATEGORY_NAMES = {
    "fault": "故障诊断",
    "sop": "维修 SOP",
    "inspection": "巡检规范",
    "safety": "安全规范",
    "chat": "普通问答",
    "guardrail": "能力边界",
    "multiturn": "多轮问答",
}


def load_test_cases():
    with open(
        TEST_CASES_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def call_agent(
    question: str,
    session_id: str,
):
    payload = {
        "text": question,
        "session_id": session_id,
    }

    data = json.dumps(
        payload,
        ensure_ascii=False,
    ).encode("utf-8")

    request = urllib.request.Request(
        API_URL,
        data=data,
        headers={
            "Content-Type": "application/json",
        },
        method="POST",
    )

    started_at = time.perf_counter()

    try:
        with urllib.request.urlopen(
            request,
            timeout=120,
        ) as response:
            body = response.read().decode(
                "utf-8"
            )

            result = json.loads(body)

    except urllib.error.HTTPError as exc:
        body = exc.read().decode(
            "utf-8",
            errors="ignore",
        )

        raise RuntimeError(
            f"HTTP {exc.code}: {body}"
        )

    except urllib.error.URLError as exc:
        raise RuntimeError(
            "无法连接 EdgeTalk Pro API，"
            "请确认 FastAPI 已在 8000 端口启动。"
        ) from exc

    elapsed_ms = round(
        (
            time.perf_counter()
            - started_at
        )
        * 1000,
        2,
    )

    if result.get("latency_ms") is None:
        result["latency_ms"] = (
            elapsed_ms
        )

    return result


def get_actual_sources(response):
    sources = response.get(
        "sources",
        [],
    )

    result = []

    for item in sources:
        if not isinstance(
            item,
            dict,
        ):
            continue

        file_name = item.get(
            "file"
        )

        if file_name:
            result.append(
                file_name
            )

    return result


def evaluate_response(
    case_id: str,
    category: str,
    question: str,
    expected_tool,
    expected_source,
    expected_guardrail,
    expected_rewrite,
    response,
):
    actual_tool = response.get(
        "tool_used"
    )

    actual_sources = (
        get_actual_sources(
            response
        )
    )

    actual_guardrail = bool(
        response.get(
            "guardrail_triggered",
            False,
        )
    )

    actual_rewrite = bool(
        response.get(
            "followup_rewritten",
            False,
        )
    )

    tool_pass = (
        expected_tool
        == actual_tool
    )

    if expected_source is None:
        source_pass = True
    else:
        source_pass = (
            expected_source
            in actual_sources
        )

    guardrail_pass = (
        bool(
            expected_guardrail
        )
        == actual_guardrail
    )

    if expected_rewrite is None:
        rewrite_pass = True
    else:
        rewrite_pass = (
            bool(
                expected_rewrite
            )
            == actual_rewrite
        )

    passed = all(
        [
            tool_pass,
            source_pass,
            guardrail_pass,
            rewrite_pass,
        ]
    )

    failures = []

    if not tool_pass:
        failures.append(
            "tool_mismatch"
        )

    if not source_pass:
        failures.append(
            "source_mismatch"
        )

    if not guardrail_pass:
        failures.append(
            "guardrail_mismatch"
        )

    if not rewrite_pass:
        failures.append(
            "rewrite_mismatch"
        )

    return {
        "id": case_id,
        "category": category,
        "category_name": (
            CATEGORY_NAMES.get(
                category,
                category,
            )
        ),
        "question": question,
        "passed": passed,
        "failures": failures,
        "expected_tool": (
            expected_tool
        ),
        "actual_tool": (
            actual_tool
        ),
        "expected_source": (
            expected_source
        ),
        "actual_sources": (
            actual_sources
        ),
        "expected_guardrail": (
            bool(
                expected_guardrail
            )
        ),
        "actual_guardrail": (
            actual_guardrail
        ),
        "expected_rewrite": (
            expected_rewrite
        ),
        "actual_rewrite": (
            actual_rewrite
        ),
        "retrieval_query": (
            response.get(
                "retrieval_query"
            )
        ),
        "latency_ms": (
            response.get(
                "latency_ms",
                0,
            )
        ),
        "answer": (
            response.get(
                "answer",
                "",
            )
        ),
    }


def run_single_case(
    test_case,
):
    case_id = test_case["id"]

    session_id = (
        f"eval_{case_id}_"
        f"{int(time.time() * 1000)}"
    )

    response = call_agent(
        question=(
            test_case[
                "question"
            ]
        ),
        session_id=session_id,
    )

    return evaluate_response(
        case_id=case_id,
        category=(
            test_case[
                "category"
            ]
        ),
        question=(
            test_case[
                "question"
            ]
        ),
        expected_tool=(
            test_case.get(
                "expected_tool"
            )
        ),
        expected_source=(
            test_case.get(
                "expected_source"
            )
        ),
        expected_guardrail=(
            test_case.get(
                "expected_guardrail",
                False,
            )
        ),
        expected_rewrite=(
            test_case.get(
                "expected_rewrite"
            )
        ),
        response=response,
    )


def run_multiturn_case(
    test_case,
):
    results = []

    case_id = test_case["id"]

    session_id = (
        f"eval_{case_id}_"
        f"{int(time.time() * 1000)}"
    )

    for index, turn in enumerate(
        test_case["turns"],
        start=1,
    ):
        turn_id = (
            f"{case_id}-T{index}"
        )

        response = call_agent(
            question=(
                turn[
                    "question"
                ]
            ),
            session_id=session_id,
        )

        result = (
            evaluate_response(
                case_id=turn_id,
                category=(
                    test_case[
                        "category"
                    ]
                ),
                question=(
                    turn[
                        "question"
                    ]
                ),
                expected_tool=(
                    turn.get(
                        "expected_tool"
                    )
                ),
                expected_source=(
                    turn.get(
                        "expected_source"
                    )
                ),
                expected_guardrail=(
                    turn.get(
                        "expected_guardrail",
                        False,
                    )
                ),
                expected_rewrite=(
                    turn.get(
                        "expected_rewrite"
                    )
                ),
                response=response,
            )
        )

        results.append(
            result
        )

    return results


def build_category_summary(
    results,
):
    category_map = {}

    for result in results:
        category = result[
            "category"
        ]

        if category not in category_map:
            category_map[category] = {
                "category": category,
                "category_name": (
                    CATEGORY_NAMES.get(
                        category,
                        category,
                    )
                ),
                "total": 0,
                "passed": 0,
                "failed": 0,
                "pass_rate": 0,
            }

        item = (
            category_map[
                category
            ]
        )

        item["total"] += 1

        if result["passed"]:
            item["passed"] += 1
        else:
            item["failed"] += 1

    for item in (
        category_map.values()
    ):
        if item["total"] > 0:
            item["pass_rate"] = round(
                (
                    item["passed"]
                    / item["total"]
                )
                * 100,
                2,
            )

    return list(
        category_map.values()
    )


def build_summary(
    results,
):
    total = len(results)

    passed = sum(
        1
        for item in results
        if item["passed"]
    )

    failed = (
        total - passed
    )

    pass_rate = (
        round(
            passed / total * 100,
            2,
        )
        if total
        else 0
    )

    latencies = [
        float(
            item.get(
                "latency_ms",
                0,
            )
        )
        for item in results
    ]

    avg_latency_ms = (
        round(
            sum(latencies)
            / len(latencies),
            2,
        )
        if latencies
        else 0
    )

    max_latency_ms = (
        round(
            max(latencies),
            2,
        )
        if latencies
        else 0
    )

    acceptance_target = 80.0

    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": pass_rate,
        "avg_latency_ms": (
            avg_latency_ms
        ),
        "max_latency_ms": (
            max_latency_ms
        ),
        "acceptance_target": (
            acceptance_target
        ),
        "accepted": (
            pass_rate
            >= acceptance_target
        ),
    }


def print_result(
    result,
):
    status = (
        "PASS"
        if result["passed"]
        else "FAIL"
    )

    print(
        f"{result['id']:<18}"
        f"{status:<8}"
        f"{result['latency_ms'] / 1000:.2f}s"
    )

    if not result["passed"]:
        print(
            "  failures:",
            ", ".join(
                result[
                    "failures"
                ]
            ),
        )


def main():
    print()
    print(
        "EdgeTalk Pro "
        "PoC Evaluation"
    )
    print(
        "=" * 50
    )

    test_cases = (
        load_test_cases()
    )

    results = []

    for test_case in test_cases:
        try:
            if (
                "turns"
                in test_case
            ):
                multi_results = (
                    run_multiturn_case(
                        test_case
                    )
                )

                for result in (
                    multi_results
                ):
                    results.append(
                        result
                    )

                    print_result(
                        result
                    )

            else:
                result = (
                    run_single_case(
                        test_case
                    )
                )

                results.append(
                    result
                )

                print_result(
                    result
                )

        except Exception as exc:
            print(
                f"{test_case['id']:<18}"
                "ERROR"
            )

            print(
                f"  {exc}"
            )

            results.append(
                {
                    "id": (
                        test_case[
                            "id"
                        ]
                    ),
                    "category": (
                        test_case[
                            "category"
                        ]
                    ),
                    "category_name": (
                        CATEGORY_NAMES.get(
                            test_case[
                                "category"
                            ],
                            test_case[
                                "category"
                            ],
                        )
                    ),
                    "question": (
                        test_case.get(
                            "question",
                            "Multi-turn test",
                        )
                    ),
                    "passed": False,
                    "failures": [
                        "execution_error"
                    ],
                    "expected_tool": None,
                    "actual_tool": None,
                    "expected_source": None,
                    "actual_sources": [],
                    "expected_guardrail": False,
                    "actual_guardrail": False,
                    "expected_rewrite": None,
                    "actual_rewrite": False,
                    "retrieval_query": None,
                    "latency_ms": 0,
                    "answer": "",
                    "error": str(exc),
                }
            )

    summary = (
        build_summary(
            results
        )
    )

    category_summary = (
        build_category_summary(
            results
        )
    )

    output = {
        "generated_at": (
            datetime.now()
            .astimezone()
            .isoformat(
                timespec="seconds"
            )
        ),
        "project": (
            "EdgeTalk Pro"
        ),
        "evaluation_version": (
            "1.0"
        ),
        "summary": summary,
        "categories": (
            category_summary
        ),
        "results": results,
    }

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        LATEST_RESULT_PATH,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            output,
            file,
            ensure_ascii=False,
            indent=2,
        )

    print()
    print(
        "=" * 50
    )

    print(
        f"Total: {summary['total']}"
    )

    print(
        f"Passed: {summary['passed']}"
    )

    print(
        f"Failed: {summary['failed']}"
    )

    print(
        "Pass Rate: "
        f"{summary['pass_rate']}%"
    )

    print(
        "Average Latency: "
        f"{summary['avg_latency_ms'] / 1000:.2f}s"
    )

    print(
        "Max Latency: "
        f"{summary['max_latency_ms'] / 1000:.2f}s"
    )

    print(
        "Acceptance: "
        + (
            "PASS"
            if summary[
                "accepted"
            ]
            else "FAIL"
        )
    )

    print()
    print(
        "Result saved to:"
    )

    print(
        LATEST_RESULT_PATH
    )


if __name__ == "__main__":
    main()
