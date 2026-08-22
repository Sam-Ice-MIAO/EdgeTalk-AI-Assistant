import {
  useEffect,
  useState,
} from "react";

import {
  Alert,
  Card,
  Col,
  Row,
  Spin,
  Statistic,
  Tag,
  Typography,
} from "antd";

import apiClient from "../api/client";

function StatusPage() {
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function fetchHealth() {
      try {
        const response =
          await apiClient.get("/health");

        setHealth(response.data);
      } catch (err) {
        console.error(err);

        setError(
          "无法连接 EdgeTalk Pro API，请确认 FastAPI 服务已经启动。"
        );
      } finally {
        setLoading(false);
      }
    }

    fetchHealth();
  }, []);

  if (loading) {
    return <Spin size="large" />;
  }

  if (error) {
    return (
      <Alert
        type="error"
        message="API Offline"
        description={error}
        showIcon
      />
    );
  }

  const components =
    health?.components || {};

  return (
    <div>
      <Typography.Title level={2}>
        System Status
      </Typography.Title>

      <Typography.Paragraph type="secondary">
        EdgeTalk Pro 后端服务和核心组件运行状态。
      </Typography.Paragraph>

      <Row gutter={[16, 16]}>
        <Col
          xs={24}
          md={8}
        >
          <Card>
            <Statistic
              title="Service"
              value={health?.service || "-"}
            />
          </Card>
        </Col>

        <Col
          xs={24}
          md={8}
        >
          <Card>
            <Statistic
              title="Version"
              value={health?.version || "-"}
            />
          </Card>
        </Col>

        <Col
          xs={24}
          md={8}
        >
          <Card>
            <Statistic
              title="Status"
              value={health?.status || "-"}
            />
          </Card>
        </Col>
      </Row>

      <Card
        title="Core Components"
        style={{ marginTop: 20 }}
      >
        <Row gutter={[16, 20]}>
          <Col xs={24} md={8}>
            API{" "}
            <Tag color="green">
              {components.api || "unknown"}
            </Tag>
          </Col>

          <Col xs={24} md={8}>
            RAG{" "}
            <Tag color="green">
              {components.rag || "unknown"}
            </Tag>
          </Col>

          <Col xs={24} md={8}>
            Agent{" "}
            <Tag color="green">
              {components.agent || "unknown"}
            </Tag>
          </Col>

          <Col xs={24} md={8}>
            Retriever{" "}
            <Tag color="blue">
              {components.retriever || "unknown"}
            </Tag>
          </Col>

          <Col xs={24} md={8}>
            Memory{" "}
            <Tag color="blue">
              {components.memory || "unknown"}
            </Tag>
          </Col>
        </Row>
      </Card>
    </div>
  );
}

export default StatusPage;
