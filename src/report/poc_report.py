from datetime import datetime
from pathlib import Path


CATEGORY_NAMES = {
    "fault": "故障诊断",
    "sop": "维修 SOP",
    "inspection": "巡检规范",
    "safety": "安全规范",
    "chat": "普通问答",
    "guardrail": "能力边界",
    "multiturn": "多轮问答",
}


def format_latency(ms):
    if not isinstance(ms, (int, float)):
        return "-"

    return f"{ms / 1000:.2f} s"


def build_overall_conclusion(summary):
    pass_rate = summary.get(
        "pass_rate",
        0,
    )

    target = summary.get(
        "acceptance_target",
        80,
    )

    accepted = summary.get(
        "accepted",
        False,
    )

    if accepted:
        return (
            f"本轮 PoC 测试通过率为 {pass_rate:.1f}%，"
            f"达到预设验收目标（≥ {target:.1f}%）。"
            "当前版本在既定测试范围内满足 PoC 验收要求。"
        )

    return (
        f"本轮 PoC 测试通过率为 {pass_rate:.1f}%，"
        f"尚未达到预设验收目标（≥ {target:.1f}%）。"
        "建议优先分析失败用例并完成针对性优化后重新评测。"
    )


def build_risk_section(results):
    failed_results = [
        item
        for item in results
        if not item.get(
            "passed",
            False,
        )
    ]

    lines = []

    if failed_results:
        lines.append(
            "### 当前 Bad Case"
        )
        lines.append("")

        for item in failed_results:
            failures = ", ".join(
                item.get(
                    "failures",
                    [],
                )
            ) or "unknown"

            lines.append(
                f"- **{item.get('id')}**："
                f"{item.get('question', '-')}"
            )

            lines.append(
                f"  - 失败原因：{failures}"
            )

        lines.append("")

    else:
        lines.append(
            "### 当前 Bad Case"
        )
        lines.append("")
        lines.append(
            "- 当前测试集中未发现失败用例。"
        )
        lines.append("")

    lines.extend(
        [
            "### 已知能力边界",
            "",
            "- 当前系统使用本地离线大模型，不具备实时互联网数据访问能力。",
            "- 天气、股票、新闻、汇率、航班、路况等实时问题由 Agent Guardrail 拦截。",
            "- 当前 PoC 测试集规模较小，测试通过率仅代表当前确定性测试范围，不等同于生产环境整体准确率。",
            "- RAG 效果依赖知识库覆盖范围、文档质量以及检索策略。",
            "- Local LLM 规模较小，复杂开放式推理能力仍存在边界。",
            "",
        ]
    )

    return "\n".join(lines)


def generate_poc_report(
    evaluation_data,
):
    summary = evaluation_data.get(
        "summary",
        {},
    )

    categories = evaluation_data.get(
        "categories",
        [],
    )

    results = evaluation_data.get(
        "results",
        [],
    )

    generated_at = evaluation_data.get(
        "generated_at",
        datetime.now()
        .astimezone()
        .isoformat(
            timespec="seconds"
        ),
    )

    report_lines = [
        "# EdgeTalk Pro PoC Evaluation Report",
        "",
        f"> Generated At: {generated_at}",
        "",
        "---",
        "",
        "## 1. 项目概述",
        "",
        "EdgeTalk Pro 是面向工业设备维护场景的本地化 AI 助手 PoC，",
        "当前能力覆盖工业知识库 RAG、Agent 路由、本地 LLM、Session Memory、",
        "Multi-turn RAG、Query Rewrite、能力边界保护与 PoC 自动化评估。",
        "",
        "本报告基于 EdgeTalk Pro 自动化 Evaluation Workflow 生成，",
        "用于记录当前版本的功能验收结果、性能指标、风险与后续优化方向。",
        "",
        "---",
        "",
        "## 2. PoC 验收目标",
        "",
        f"- 预设通过率目标：**≥ {summary.get('acceptance_target', 80):.1f}%**",
        "- 验证 Agent 工具路由是否符合预期",
        "- 验证 RAG 是否命中预期知识来源",
        "- 验证 Multi-turn Query Rewrite 是否正确触发",
        "- 验证实时信息 Guardrail 是否正确触发",
        "- 记录接口响应延迟",
        "",
        "---",
        "",
        "## 3. 整体评估结果",
        "",
        "| 指标 | 结果 |",
        "| --- | ---: |",
        f"| 测试请求数 | {summary.get('total', 0)} |",
        f"| 通过数 | {summary.get('passed', 0)} |",
        f"| 失败数 | {summary.get('failed', 0)} |",
        f"| 通过率 | {summary.get('pass_rate', 0):.1f}% |",
        f"| 平均延迟 | {format_latency(summary.get('avg_latency_ms'))} |",
        f"| 最大延迟 | {format_latency(summary.get('max_latency_ms'))} |",
        f"| PoC 验收结果 | {'PASS' if summary.get('accepted') else 'FAIL'} |",
        "",
        "### 验收结论",
        "",
        build_overall_conclusion(
            summary
        ),
        "",
        "---",
        "",
        "## 4. 分类测试结果",
        "",
        "| 场景 | 通过 | 总数 | 通过率 |",
        "| --- | ---: | ---: | ---: |",
    ]

    for category in categories:
        name = category.get(
            "category_name"
        ) or CATEGORY_NAMES.get(
            category.get(
                "category"
            ),
            category.get(
                "category",
                "-",
            ),
        )

        report_lines.append(
            f"| {name} | "
            f"{category.get('passed', 0)} | "
            f"{category.get('total', 0)} | "
            f"{category.get('pass_rate', 0):.1f}% |"
        )

    report_lines.extend(
        [
            "",
            "---",
            "",
            "## 5. 性能指标",
            "",
            f"- 平均响应延迟：**{format_latency(summary.get('avg_latency_ms'))}**",
            f"- 最大响应延迟：**{format_latency(summary.get('max_latency_ms'))}**",
            "",
            "说明：本地模型的首次请求可能受到模型加载、Embedding 初始化或缓存预热影响，",
            "稳定运行后的请求延迟通常会低于首次请求。",
            "",
            "---",
            "",
            "## 6. 测试明细",
            "",
            "| ID | 场景 | 问题 | 结果 | Tool | Source | Rewrite | Latency |",
            "| --- | --- | --- | --- | --- | --- | --- | ---: |",
        ]
    )

    for item in results:
        sources = item.get(
            "actual_sources",
            [],
        )

        source_text = (
            ", ".join(sources)
            if sources
            else "-"
        )

        question = (
            item.get(
                "question",
                "-",
            )
            .replace("|", "\\|")
            .replace("\n", " ")
        )

        report_lines.append(
            f"| {item.get('id', '-')} "
            f"| {item.get('category_name', '-')} "
            f"| {question} "
            f"| {'PASS' if item.get('passed') else 'FAIL'} "
            f"| {item.get('actual_tool') or '-'} "
            f"| {source_text} "
            f"| {'Yes' if item.get('actual_rewrite') else '-'} "
            f"| {format_latency(item.get('latency_ms'))} |"
        )

    report_lines.extend(
        [
            "",
            "---",
            "",
            "## 7. 风险与 Bad Case",
            "",
            build_risk_section(
                results
            ),
            "---",
            "",
            "## 8. PoC 验收结论",
            "",
            build_overall_conclusion(
                summary
            ),
            "",
            "---",
            "",
            "## 9. 后续建议",
            "",
            "1. 扩充工业设备知识库与真实故障案例，提高场景覆盖率。",
            "2. 扩大 Evaluation Test Set，避免当前小规模测试集导致结果过于乐观。",
            "3. 对冷启动和首请求延迟进行服务预热与缓存优化。",
            "4. 如需实时天气、设备云状态或外部业务数据，可通过 Agent Tool 接入对应 API。",
            "5. 后续可进一步增加云端部署、监控和更完整的 PoC 报告导出能力。",
            "",
            "---",
            "",
            "*This report was automatically generated by EdgeTalk Pro PoC Evaluation Workflow.*",
            "",
        ]
    )

    return "\n".join(
        report_lines
    )


def save_poc_report(
    evaluation_data,
    output_path,
):
    report = generate_poc_report(
        evaluation_data
    )

    path = Path(
        output_path
    )

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        report,
        encoding="utf-8",
    )

    return path
