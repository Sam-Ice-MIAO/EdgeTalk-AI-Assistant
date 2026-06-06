from src.agent.tools import (
    list_knowledge_files,
    search_knowledge,
    get_project_status,
)


def main():
    print("===== 测试 1：列出知识库文件 =====")
    file_result = list_knowledge_files()
    print(file_result)
    print()

    print("===== 测试 2：检索知识库 =====")
    search_result = search_knowledge("EdgeTalk 当前实现了哪些功能？")
    print(search_result)
    print()

    print("===== 测试 3：查看项目状态 =====")
    status_result = get_project_status()
    print(status_result)


if __name__ == "__main__":
    main()
