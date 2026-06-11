from src.agent.agent_core import AgentCore


def main():
    agent = AgentCore()

    session_id = "day3_memory_test"

    questions = [
        "E03 报警是什么意思？",
        "更换温度传感器前需要做哪些准备？",
    ]

    for question in questions:
        print("=" * 80)
        print("用户问题：", question)

        result = agent.run(
            user_text=question,
            session_id=session_id,
        )

        print("使用工具：", result.get("tool_used"))
        print("回答：", result.get("answer"))

    print("=" * 80)
    print("当前会话记忆：")

    messages = agent.memory.get_recent_messages(
        session_id=session_id,
        limit=10,
    )

    for msg in messages:
        print(f"[{msg['role']}] {msg['content']}")


if __name__ == "__main__":
    main()
