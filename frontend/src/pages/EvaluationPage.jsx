import {
  useEffect,
  useState,
} from "react";

import {
  Alert,
  Card,
  Col,
  Empty,
  Progress,
  Row,
  Spin,
  Statistic,
  Table,
  Tag,
  Typography,
} from "antd";

import {
  getLatestEvaluation,
} from "../api/evaluation";


function EvaluationPage() {
  const [
    data,
    setData,
  ] = useState(null);

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    error,
    setError,
  ] = useState("");


  useEffect(() => {
    async function loadEvaluation() {
      try {
        const result =
          await getLatestEvaluation();

        setData(result);

      } catch (err) {
        console.error(err);

        setError(
          "暂时没有可用的 PoC 评估结果，请先运行 python eval/run_eval.py。"
        );

      } finally {
        setLoading(false);
      }
    }

    loadEvaluation();
  }, []);


  if (loading) {
    return (
      <Spin size="large" />
    );
  }


  if (error) {
    return (
      <Alert
        type="warning"
        showIcon
        message="Evaluation Result Not Found"
        description={error}
      />
    );
  }


  if (!data) {
    return (
      <Empty
        description="暂无评估结果"
      />
    );
  }


  const summary =
    data.summary || {};

  const categories =
    data.categories || [];

  const results =
    data.results || [];


  const columns = [
    {
      title: "ID",
      dataIndex: "id",
      key: "id",
      width: 130,
    },
    {
      title: "场景",
      dataIndex:
        "category_name",
      key: "category_name",
      width: 110,
    },
    {
      title: "问题",
      dataIndex: "question",
      key: "question",
      ellipsis: true,
    },
    {
      title: "结果",
      dataIndex: "passed",
      key: "passed",
      width: 90,
      render: (passed) => (
        <Tag
          color={
            passed
              ? "green"
              : "red"
          }
        >
          {passed
            ? "PASS"
            : "FAIL"}
        </Tag>
      ),
    },
    {
      title: "Tool",
      dataIndex:
        "actual_tool",
      key: "actual_tool",
      width: 150,
      render: (value) => (
        <Tag color="blue">
          {value || "-"}
        </Tag>
      ),
    },
    {
      title: "Source",
      dataIndex:
        "actual_sources",
      key: "actual_sources",
      width: 180,
      render: (sources) => {
        if (
          !sources ||
          sources.length === 0
        ) {
          return "-";
        }

        return sources.join(
          ", "
        );
      },
    },
    {
      title: "Rewrite",
      dataIndex:
        "actual_rewrite",
      key: "actual_rewrite",
      width: 90,
      render: (value) => (
        value
          ? (
            <Tag color="purple">
              Yes
            </Tag>
          )
          : "-"
      ),
    },
    {
      title: "Latency",
      dataIndex:
        "latency_ms",
      key: "latency_ms",
      width: 100,
      render: (value) => (
        typeof value === "number"
          ? `${(
              value / 1000
            ).toFixed(2)}s`
          : "-"
      ),
    },
  ];


  return (
    <div>
      <Typography.Title
        level={2}
      >
        PoC Evaluation
      </Typography.Title>

      <Typography.Paragraph
        type="secondary"
      >
        对 EdgeTalk Pro 的 Agent 路由、RAG 来源命中、
        多轮 Query Rewrite、能力边界保护和响应延迟进行自动化验证。
      </Typography.Paragraph>


      <Row
        gutter={[
          16,
          16,
        ]}
      >
        <Col
          xs={24}
          md={12}
          lg={6}
        >
          <Card>
            <Statistic
              title="Test Cases"
              value={
                summary.total || 0
              }
            />
          </Card>
        </Col>

        <Col
          xs={24}
          md={12}
          lg={6}
        >
          <Card>
            <Statistic
              title="Passed"
              value={
                summary.passed || 0
              }
            />
          </Card>
        </Col>

        <Col
          xs={24}
          md={12}
          lg={6}
        >
          <Card>
            <Statistic
              title="Pass Rate"
              value={
                summary.pass_rate || 0
              }
              suffix="%"
              precision={1}
            />
          </Card>
        </Col>

        <Col
          xs={24}
          md={12}
          lg={6}
        >
          <Card>
            <Statistic
              title="Avg Latency"
              value={
                (
                  summary.avg_latency_ms ||
                  0
                ) / 1000
              }
              suffix="s"
              precision={2}
            />
          </Card>
        </Col>
      </Row>


      <Card
        title="PoC Acceptance"
        style={{
          marginTop: 20,
        }}
      >
        <Row
          gutter={[
            24,
            16,
          ]}
          align="middle"
        >
          <Col
            xs={24}
            md={8}
          >
            <Statistic
              title="Acceptance Target"
              value={
                summary
                  .acceptance_target ||
                80
              }
              suffix="%"
            />
          </Col>

          <Col
            xs={24}
            md={8}
          >
            <Statistic
              title="Current Result"
              value={
                summary.pass_rate ||
                0
              }
              suffix="%"
              precision={1}
            />
          </Col>

          <Col
            xs={24}
            md={8}
          >
            <Typography.Text
              strong
            >
              Result
            </Typography.Text>

            <div
              style={{
                marginTop: 8,
              }}
            >
              <Tag
                color={
                  summary.accepted
                    ? "green"
                    : "red"
                }
              >
                {summary.accepted
                  ? "PASS"
                  : "FAIL"}
              </Tag>
            </div>
          </Col>
        </Row>
      </Card>


      <Card
        title="Category Performance"
        style={{
          marginTop: 20,
        }}
      >
        <Row
          gutter={[
            24,
            20,
          ]}
        >
          {categories.map(
            (item) => (
              <Col
                xs={24}
                md={12}
                lg={8}
                key={
                  item.category
                }
              >
                <Typography.Text
                  strong
                >
                  {
                    item.category_name
                  }
                </Typography.Text>

                <Progress
                  percent={
                    item.pass_rate
                  }
                  status={
                    item.pass_rate >=
                    80
                      ? "success"
                      : "exception"
                  }
                  style={{
                    marginTop: 8,
                  }}
                />

                <Typography.Text
                  type="secondary"
                >
                  {item.passed} /{" "}
                  {item.total} Passed
                </Typography.Text>
              </Col>
            )
          )}
        </Row>
      </Card>


      <Card
        title="Performance"
        style={{
          marginTop: 20,
        }}
      >
        <Row
          gutter={[
            16,
            16,
          ]}
        >
          <Col
            xs={24}
            md={12}
          >
            <Statistic
              title="Average Latency"
              value={
                (
                  summary.avg_latency_ms ||
                  0
                ) / 1000
              }
              suffix="s"
              precision={2}
            />
          </Col>

          <Col
            xs={24}
            md={12}
          >
            <Statistic
              title="Max Latency"
              value={
                (
                  summary.max_latency_ms ||
                  0
                ) / 1000
              }
              suffix="s"
              precision={2}
            />
          </Col>
        </Row>
      </Card>


      <Card
        title="Test Details"
        style={{
          marginTop: 20,
        }}
      >
        <Table
          rowKey="id"
          columns={columns}
          dataSource={results}
          pagination={{
            pageSize: 8,
          }}
          scroll={{
            x: 1100,
          }}
        />
      </Card>


      <Typography.Text
        type="secondary"
        style={{
          display: "block",
          marginTop: 16,
        }}
      >
        Generated At:{" "}
        {data.generated_at ||
          "-"}
      </Typography.Text>
    </div>
  );
}


export default EvaluationPage;
