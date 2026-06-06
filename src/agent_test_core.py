from src.pipeline import EdgeTalkPipeline
from src.agent.agent_core import AgentCore


def main():
    pipeline = EdgeTalkPipeline()
    agent = AgentCore(pipeline=pipeline)

    questions = [
        "知识库里有哪些文档？",
        "EdgeTalk 当前实现了哪些功能？",
        "请介绍一下你自己。"
    ]

    for question in questions:
        print("=" * 60)
        result = agent.run(question)

        print("问题:", result["input"])
        print("使用工具:", result["tool_used"])
        print("回答:", result["answer"])
        print("工具结果:", result["tool_result"])


if __name__ == "__main__":
    main()
