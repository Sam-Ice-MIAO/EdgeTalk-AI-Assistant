import {
  Card,
  Col,
  Row,
  Tag,
  Typography,
} from "antd";

const knowledgeItems = [
  {
    title: "设备手册",
    description: "工业设备基础说明与操作资料",
  },
  {
    title: "故障码表",
    description: "设备故障代码、原因与处理建议",
  },
  {
    title: "维修 SOP",
    description: "标准维修流程与部件更换步骤",
  },
  {
    title: "巡检清单",
    description: "设备每日点检与巡检项目",
  },
  {
    title: "安全规范",
    description: "设备维护相关安全操作要求",
  },
];

function KnowledgePage() {
  return (
    <div>
      <Typography.Title level={2}>
        Industrial Knowledge Base
      </Typography.Title>

      <Typography.Paragraph type="secondary">
        EdgeTalk Pro 当前接入的工业设备维护知识库。
      </Typography.Paragraph>

      <Row gutter={[16, 16]}>
        {knowledgeItems.map((item) => (
          <Col
            xs={24}
            md={12}
            lg={8}
            key={item.title}
          >
            <Card title={item.title}>
              <Typography.Paragraph>
                {item.description}
              </Typography.Paragraph>

              <Tag color="green">
                Ready
              </Tag>
            </Card>
          </Col>
        ))}
      </Row>
    </div>
  );
}

export default KnowledgePage;
