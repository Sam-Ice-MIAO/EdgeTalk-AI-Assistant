import json
import sys
import time
import urllib.error
import urllib.request


BASE_URL = "http://127.0.0.1:8000"


def request_json(
    method: str,
    path: str,
    payload=None,
):
    url = BASE_URL + path

    data = None

    headers = {
        "Content-Type": "application/json",
    }

    if payload is not None:
        data = json.dumps(
            payload,
            ensure_ascii=False,
        ).encode("utf-8")

    request = urllib.request.Request(
        url=url,
        data=data,
        headers=headers,
        method=method,
    )

    started_at = time.perf_counter()

    try:
        with urllib.request.urlopen(
            request,
            timeout=120,
        ) as response:
            result = json.loads(
                response
                .read()
                .decode("utf-8")
            )

    except urllib.error.HTTPError as exc:
        body = (
            exc.read()
            .decode(
                "utf-8",
                errors="ignore",
            )
        )

        raise RuntimeError(
            f"HTTP {exc.code}: {body}"
        )

    except urllib.error.URLError as exc:
        raise RuntimeError(
            "无法连接 FastAPI，"
            "请确认 8000 端口已经启动。"
        ) from exc

    elapsed_ms = round(
        (
            time.perf_counter()
            - started_at
        )
        * 1000,
        2,
    )

    return result, elapsed_ms


def check(
    name: str,
    condition: bool,
    detail: str = "",
):
    if condition:
        print(
            f"[PASS] {name}"
        )

        if detail:
            print(
                f"       {detail}"
            )

        return True

    print(
        f"[FAIL] {name}"
    )

    if detail:
        print(
            f"       {detail}"
        )

    return False


def test_health():
    result, latency = request_json(
        "GET",
        "/health",
    )

    passed = (
        result.get("status")
        == "healthy"
    )

    return check(
        "Health API",
        passed,
        (
            f"status={result.get('status')} "
            f"latency={latency:.0f}ms"
        ),
    )


def test_rag():
    session_id = (
        f"smoke_rag_"
        f"{int(time.time() * 1000)}"
    )

    result, latency = request_json(
        "POST",
        "/agent-chat",
        {
            "text":
                "E03报警是什么意思？",
            "session_id":
                session_id,
        },
    )

    files = [
        item.get("file")
        for item in result.get(
            "sources",
            [],
        )
        if isinstance(
            item,
            dict,
        )
    ]

    passed = (
        result.get("tool_used")
        == "search_knowledge"
        and
        "fault_codes.txt"
        in files
    )

    return check(
        "Industrial RAG",
        passed,
        (
            f"tool="
            f"{result.get('tool_used')} "
            f"source={files} "
            f"latency={latency:.0f}ms"
        ),
    )


def test_multiturn():
    session_id = (
        f"smoke_multi_"
        f"{int(time.time() * 1000)}"
    )

    first_result, _ = request_json(
        "POST",
        "/agent-chat",
        {
            "text":
                "E03报警是什么意思？",
            "session_id":
                session_id,
        },
    )

    first_files = [
        item.get("file")
        for item in first_result.get(
            "sources",
            [],
        )
        if isinstance(
            item,
            dict,
        )
    ]

    first_passed = (
        first_result.get(
            "tool_used"
        )
        == "search_knowledge"
        and
        "fault_codes.txt"
        in first_files
    )

    if not first_passed:
        return check(
            "Multi-turn RAG",
            False,
            (
                "first turn failed: "
                f"tool="
                f"{first_result.get('tool_used')} "
                f"source={first_files}"
            ),
        )

    result, latency = request_json(
        "POST",
        "/agent-chat",
        {
            "text":
                "那我第一步该检查什么？",
            "session_id":
                session_id,
        },
    )

    files = [
        item.get("file")
        for item in result.get(
            "sources",
            [],
        )
        if isinstance(
            item,
            dict,
        )
    ]

    retrieval_query = (
        result.get(
            "retrieval_query"
        )
        or ""
    )

    passed = (
        result.get(
            "followup_rewritten"
        )
        is True
        and
        "fault_codes.txt"
        in files
        and
        "E03"
        in retrieval_query
    )

    return check(
        "Multi-turn RAG",
        passed,
        (
            "rewrite="
            f"{result.get('followup_rewritten')} "
            f"source={files} "
            f"latency={latency:.0f}ms"
        ),
    )


def test_guardrail():
    session_id = (
        f"smoke_guard_"
        f"{int(time.time() * 1000)}"
    )

    result, latency = request_json(
        "POST",
        "/agent-chat",
        {
            "text":
                "北京明天天气怎么样？",
            "session_id":
                session_id,
        },
    )

    passed = (
        result.get(
            "tool_used"
        )
        == "realtime_guard"
        and
        result.get(
            "guardrail_triggered"
        )
        is True
    )

    return check(
        "Realtime Guardrail",
        passed,
        (
            f"tool="
            f"{result.get('tool_used')} "
            "triggered="
            f"{result.get('guardrail_triggered')} "
            f"latency={latency:.0f}ms"
        ),
    )


def test_chat():
    session_id = (
        f"smoke_chat_"
        f"{int(time.time() * 1000)}"
    )

    result, latency = request_json(
        "POST",
        "/agent-chat",
        {
            "text":
                "什么是预测性维护？",
            "session_id":
                session_id,
        },
    )

    answer = (
        result.get("answer")
        or ""
    )

    passed = (
        result.get(
            "tool_used"
        )
        == "chat"
        and
        bool(
            answer.strip()
        )
    )

    return check(
        "Local LLM Chat",
        passed,
        (
            f"tool="
            f"{result.get('tool_used')} "
            f"answer_length="
            f"{len(answer)} "
            f"latency={latency:.0f}ms"
        ),
    )


def test_evaluation_api():
    result, latency = request_json(
        "GET",
        "/evaluation/latest",
    )

    summary = (
        result.get(
            "summary"
        )
        or {}
    )

    total = summary.get(
        "total",
        0,
    )

    passed_count = (
        summary.get(
            "passed",
            0,
        )
    )

    pass_rate = (
        summary.get(
            "pass_rate",
            0,
        )
    )

    accepted = (
        summary.get(
            "accepted",
            False,
        )
    )

    passed = (
        total > 0
        and
        passed_count > 0
        and
        accepted is True
    )

    return check(
        "Evaluation API",
        passed,
        (
            f"tests={total} "
            f"passed={passed_count} "
            f"pass_rate={pass_rate}% "
            f"accepted={accepted} "
            f"latency={latency:.0f}ms"
        ),
    )


def test_report_api():
    result, latency = request_json(
        "GET",
        "/evaluation/report",
    )

    report = (
        result.get(
            "report"
        )
        or ""
    )

    report_format = (
        result.get(
            "report_format"
        )
    )

    passed = (
        result.get(
            "success"
        )
        is True
        and
        report_format
        == "markdown"
        and
        "EdgeTalk Pro"
        in report
        and
        "PoC"
        in report
        and
        "验收"
        in report
    )

    return check(
        "PoC Report API",
        passed,
        (
            f"format="
            f"{report_format} "
            f"report_length="
            f"{len(report)} "
            f"latency={latency:.0f}ms"
        ),
    )


def main():
    print()
    print(
        "EdgeTalk Pro Smoke Test"
    )

    print(
        "=" * 60
    )

    tests = [
        test_health,
        test_rag,
        test_multiturn,
        test_guardrail,
        test_chat,
        test_evaluation_api,
        test_report_api,
    ]

    results = []

    for test in tests:
        try:
            result = test()

            results.append(
                result
            )

        except Exception as exc:
            print(
                f"[ERROR] "
                f"{test.__name__}"
            )

            print(
                f"        {exc}"
            )

            results.append(
                False
            )

        print()

    passed = sum(
        1
        for item in results
        if item
    )

    total = len(
        results
    )

    print(
        "=" * 60
    )

    print(
        f"Passed: "
        f"{passed}/{total}"
    )

    if passed == total:
        print(
            "Smoke Test: PASS"
        )

        sys.exit(0)

    print(
        "Smoke Test: FAIL"
    )

    sys.exit(1)


if __name__ == "__main__":
    main()
