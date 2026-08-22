import { useMemo, useState } from "react";

import {
  Alert,
  Button,
  Card,
  Col,
  Empty,
  Input,
  Row,
  Space,
  Spin,
  Tag,
  Typography,
} from "antd";

import {
  RobotOutlined,
  SendOutlined,
  UserOutlined,
} from "@ant-design/icons";

import { sendAgentMessage } from "../api/chat";

const { TextArea } = Input;

const quickQuestions = [
  {
    label: "故障诊断",
    question: "E03 报警是什么意思？",
  },
  {
    label: "维修 SOP",
    question: "更换传感器之前需要注意什么？",
  },
  {
    label: "每日点检",
    question: "每日点检需要检查哪些项目？",
  },
  {
    label: "安全规范",
    question: "设备维修前有哪些安全注意事项？",
  },
];

function ChatPage() {
  const sessionId = useMemo(
    () => `web_${Date.now()}`,
    []
  );

  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [latestResult, setLatestResult] = useState(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSend(customText) {
    const question =
      typeof customText === "string"
        ? customText.trim()
        : input.trim();

    if (!question || loading) {
      return;
    }

    setError("");
    setInput("");

    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        content: question,
      },
    ]);

    setLoading(true);

    try {
      const result = await sendAgentMessage(
        question,
        sessionId
      );

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            result.answer ||
            "系统未返回有效回答。",
        },
      ]);

      setLatestResult(result);
    } catch (err) {
      console.error(err);
      const errorMessage =
        "EdgeTalk Pro 后端服务暂时不可用，请确认 FastAPI 服务已经启动。";

      setError(errorMessage);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `⚠ ${errorMessage}`,
        },
      ]);
    }        
      finally {
      setLoading(false);
    }
  }

  function handleKeyDown(event) {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();
      handleSend();
    }
  }

  const sources =
    latestResult?.sources || [];

  return (
    <div>
      <Typography.Title level={2}>
        AI Assistant
      </Typography.Title>

      <Typography.Paragraph type="secondary">
        面向工业设备故障诊断、维修 SOP、
        每日点检和安全规范场景的智能维护助手。
      </Typography.Paragraph>

      <Space
        wrap
        style={{ marginBottom: 20 }}
      >
        {quickQuestions.map((item) => (
          <Button
            key={item.label}
            onClick={() =>
              handleSend(item.question)
            }
            disabled={loading}
          >
            {item.label}
          </Button>
        ))}
      </Space>

      {error && (
        <Alert
          type="error"
          message="请求失败"
          description={error}
          showIcon
          closable
          onClose={() => setError("")}
          style={{ marginBottom: 20 }}
        />
      )}

      <Row gutter={[20, 20]}>
        <Col
          xs={24}
          lg={16}
        >
          <Card title="EdgeTalk 对话">
            <div className="chat-container">
              {messages.length === 0 ? (
                <Empty
                  description="请输入设备维护问题开始对话"
                />
              ) : (
                messages.map((message, index) => (
                  <div
                    key={index}
                    className={`chat-message ${message.role}`}
                  >
                    <div className="message-role">
                      {message.role === "user" ? (
                        <>
                          <UserOutlined />
                          用户
                        </>
                      ) : (
                        <>
                          <RobotOutlined />
                          EdgeTalk
                        </>
                      )}
                    </div>

                    <div className="message-content">
                      {message.content}
                    </div>
                  </div>
                ))
              )}

              {loading && (
                <div className="chat-loading">
                  <Spin size="small" />
                  <Typography.Text
                    type="secondary"
                  >
                    正在检索工业知识库并生成回答……
                  </Typography.Text>
                </div>
              )}
            </div>

            <div className="chat-input-area">
              <TextArea
                value={input}
                onChange={(event) =>
                  setInput(event.target.value)
                }
                onKeyDown={handleKeyDown}
                rows={3}
                placeholder="例如：E03 报警是什么意思？"
                disabled={loading}
              />

              <Button
                type="primary"
                icon={<SendOutlined />}
                loading={loading}
                onClick={() => handleSend()}
                style={{ marginTop: 12 }}
              >
                发送
              </Button>
            </div>
          </Card>
        </Col>

        <Col
          xs={24}
          lg={8}
        >
          <Card title="Knowledge Evidence">
            {!latestResult ? (
              <Empty
                description="暂无检索结果"
              />
            ) : (
              <>
                <div className="evidence-meta">
                  <div>
                    <Typography.Text strong>
                      Tool
                    </Typography.Text>

                    <div>
                      <Tag color="blue">
                        {latestResult.tool_used ||
                          "none"}
                      </Tag>
                    </div>
                  </div>

                  <div>
                    <Typography.Text strong>
                      Retriever
                    </Typography.Text>

                    <div>
                      <Tag color="blue">
                        {latestResult.retriever_type ||
                          "none"}
                      </Tag>
                    </div>
                  </div>

                  <div>
                    <Typography.Text strong>
                      Latency
                    </Typography.Text>

                    <div>
                      {latestResult.latency_ms
                        ? `${(
                            latestResult.latency_ms /
                            1000
                          ).toFixed(2)} s`
                        : "-"}
                    </div>
                  </div>
                </div>

                <Typography.Title
                  level={5}
                  style={{ marginTop: 24 }}
                >
                  Sources
                </Typography.Title>

                {sources.length === 0 ? (
                  <Typography.Text type="secondary">
                    本次回答未使用知识库检索。
                  </Typography.Text>
                ) : (
                  sources.map((source, index) => (
                    <Card
                      key={`${source.source}-${index}`}
                      size="small"
                      style={{ marginBottom: 12 }}
                    >
                      <Typography.Text strong>
                        {source.file ||
                          "Unknown Source"}
                      </Typography.Text>

                      <div
                        style={{
                          marginTop: 8,
                          marginBottom: 8,
                        }}
                      >
                        <Tag>
                          Chunk {source.chunk_id}
                        </Tag>

                        {typeof source.score ===
                          "number" && (
                          <Tag color="green">
                            Score{" "}
                            {source.score.toFixed(4)}
                          </Tag>
                        )}
                      </div>

                      <Typography.Paragraph
                        ellipsis={{
                          rows: 8,
                          expandable: true,
                          symbol: "展开",
                        }}
                        style={{
                          whiteSpace: "pre-wrap",
                          marginBottom: 0,
                        }}
                      >
                        {source.text}
                      </Typography.Paragraph>
                    </Card>
                  ))
                )}

                <Typography.Text
                  type="secondary"
                  style={{
                    display: "block",
                    marginTop: 16,
                  }}
                >
                  Session:{" "}
                  {latestResult.session_id}
                </Typography.Text>
              </>
            )}
          </Card>
        </Col>
      </Row>
    </div>
  );
}

export default ChatPage;
