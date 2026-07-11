from src.memory.sqlite_memory import SQLiteMemory


def main():
    memory = SQLiteMemory()

    session_id = "test_session"

    memory.save_message(
        session_id=session_id,
        role="user",
        content="EdgeTalk 当前实现了哪些功能？"
    )

    memory.save_message(
        session_id=session_id,
        role="assistant",
        content="EdgeTalk 当前支持文本问答、语音问答、FastAPI 接口和 RAG 本地知识库问答。"
    )

    messages = memory.get_recent_messages(session_id=session_id, limit=6)

    print("最近对话记录：")
    for message in messages:
        print(message["created_at"], message["role"], ":", message["content"])


if __name__ == "__main__":
    main()
