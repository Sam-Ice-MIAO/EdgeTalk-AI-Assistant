import {
  Button,
  Card,
  Input,
  Space,
  Tag,
  Typography,
} from "antd";

const { TextArea } = Input;

function ChatPage() {
  return (
    <div>
      <Typography.Title level={2}>
        AI Assistant
      </Typography.Title>

      <Typography.Paragraph type="secondary">
        面向工业设备故障诊断、维修 SOP、每日点检和安全规范场景的智能维护助手。
      </Typography.Paragraph>

      <Space
        wrap
        style={{ marginBottom: 20 }}
      >
        <Tag color="blue">
          故障诊断
        </Tag>

        <Tag color="blue">
          维修 SOP
        </Tag>

        <Tag color="blue">
          每日点检
        </Tag>

        <Tag color="blue">
          安全规范
        </Tag>
      </Space>

      <Card title="EdgeTalk 对话">
        <div className="chat-placeholder">
          <Typography.Text type="secondary">
            EdgeTalk Pro 已准备就绪。
            请在下方输入设备维护问题。
          </Typography.Text>
        </div>

        <TextArea
          rows={4}
          placeholder="例如：E03 报警是什么意思？"
          style={{ marginTop: 20 }}
        />

        <Button
          type="primary"
          style={{ marginTop: 12 }}
        >
          发送
        </Button>
      </Card>
    </div>
  );
}

export default ChatPage;
