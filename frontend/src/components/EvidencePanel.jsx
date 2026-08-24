import {
  Alert,
  Card,
  Collapse,
  Empty,
  Progress,
  Space,
  Tag,
  Typography,
} from "antd";

const sourceNames = {
  "fault_codes.txt": "故障码表",
  "maintenance_sop.txt": "维修 SOP",
  "inspection_checklist.txt": "巡检清单",
  "safety_rules.txt": "安全规范",
  "equipment_manual.txt": "设备手册",
};

function getSourceName(file) {
  return (
    sourceNames[file] ||
    "工业知识文档"
  );
}

function getScoreStatus(score) {
  if (
    typeof score !== "number"
  ) {
    return {
      text: "未知",
      status: "normal",
    };
  }

  if (score >= 0.7) {
    return {
      text: "高相关",
      status: "success",
    };
  }

  if (score >= 0.5) {
    return {
      text: "中等相关",
      status: "normal",
    };
  }

  return {
    text: "低相关",
    status: "exception",
  };
}

function EvidencePanel({
  result,
}) {
  if (!result) {
    return (
      <Card title="回答依据">
        <Empty
          description={
            "发送问题后将在这里显示知识库检索依据"
          }
        />
      </Card>
    );
  }

  const sources =
    result.sources || [];

  return (
    <Card title="回答依据">
      <Space
        wrap
        size={[8, 8]}
      >
        <Tag color="blue">
          Tool:{" "}
          {result.tool_used ||
            "none"}
        </Tag>

        <Tag color="geekblue">
          Retriever:{" "}
          {result.retriever_type ||
            "none"}
        </Tag>

        <Tag>
          Latency:{" "}
          {typeof
            result.latency_ms ===
          "number"
            ? `${(
                result.latency_ms /
                1000
              ).toFixed(2)} s`
            : "-"}
        </Tag>
      </Space>

      {result.followup_rewritten &&
        result.retrieval_query && (
          <div className="rewrite-box">
            <Typography.Text strong>
              多轮检索改写
            </Typography.Text>

            <Typography.Paragraph
              type="secondary"
              style={{
                marginTop: 8,
                marginBottom: 0,
                whiteSpace:
                  "pre-wrap",
              }}
            >
              {
                result.retrieval_query
              }
            </Typography.Paragraph>
          </div>
        )}

      {result.guardrail_triggered && (
        <Alert
          type="warning"
          showIcon
          message="能力边界保护已触发"
          description={
            "该问题需要实时外部数据，当前本地模型未接入对应实时数据源。"
          }
          style={{
            marginTop: 16,
          }}
        />
      )}

      <Typography.Title
        level={5}
        style={{
          marginTop: 22,
        }}
      >
        Knowledge Sources
      </Typography.Title>

      {sources.length === 0 ? (
        <Typography.Text
          type="secondary"
        >
          本次回答未调用知识库检索结果。
        </Typography.Text>
      ) : (
        sources.map(
          (
            source,
            index
          ) => {
            const score =
              typeof
                source.score ===
              "number"
                ? source.score
                : null;

            const percentage =
              score !== null
                ? Math.min(
                    100,
                    Math.max(
                      0,
                      score * 100
                    )
                  )
                : 0;

            const scoreStatus =
              getScoreStatus(
                score
              );

            return (
              <Card
                key={`${source.source}-${index}`}
                size="small"
                className="evidence-source-card"
              >
                <div className="source-title-row">
                  <div>
                    <Typography.Text
                      strong
                    >
                      {getSourceName(
                        source.file
                      )}
                    </Typography.Text>

                    <div>
                      <Typography.Text
                        type="secondary"
                        className="source-file-name"
                      >
                        {source.file}
                      </Typography.Text>
                    </div>
                  </div>

                  <Tag>
                    {
                      scoreStatus.text
                    }
                  </Tag>
                </div>

                <div className="score-section">
                  <Typography.Text>
                    检索相关度
                  </Typography.Text>

                  <Progress
                    percent={Number(
                      percentage.toFixed(
                        1
                      )
                    )}
                    status={
                      scoreStatus.status
                    }
                  />
                </div>

                <Typography.Text
                  strong
                >
                  检索内容
                </Typography.Text>

                <Typography.Paragraph
                  ellipsis={{
                    rows: 7,
                    expandable: true,
                    symbol:
                      "展开原文",
                  }}
                  className="source-text"
                >
                  {source.text ||
                    "-"}
                </Typography.Paragraph>

                <Collapse
                  ghost
                  size="small"
                  items={[
                    {
                      key:
                        "technical",
                      label:
                        "技术详情",
                      children: (
                        <div className="technical-details">
                          <div>
                            Chunk ID：
                            {source.chunk_id ??
                              "-"}
                          </div>

                          <div>
                            Final
                            Score：
                            {typeof
                              source.score ===
                            "number"
                              ? source.score.toFixed(
                                  4
                                )
                              : "-"}
                          </div>

                          <div>
                            Raw Score：
                            {typeof
                              source.raw_score ===
                            "number"
                              ? source.raw_score.toFixed(
                                  4
                                )
                              : "-"}
                          </div>

                          <div>
                            Rule Boost：
                            {typeof
                              source.boost ===
                            "number"
                              ? source.boost.toFixed(
                                  4
                                )
                              : "-"}
                          </div>

                          <div>
                            Source：
                            {source.source ||
                              "-"}
                          </div>
                        </div>
                      ),
                    },
                  ]}
                />
              </Card>
            );
          }
        )
      )}

      <Typography.Text
        type="secondary"
        style={{
          display: "block",
          marginTop: 16,
        }}
      >
        Session:{" "}
        {result.session_id ||
          "-"}
      </Typography.Text>
    </Card>
  );
}

export default EvidencePanel;
