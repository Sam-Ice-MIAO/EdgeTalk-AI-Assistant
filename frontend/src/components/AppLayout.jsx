import {
  BarChartOutlined,
  DashboardOutlined,
  DatabaseOutlined,
  RobotOutlined,
} from "@ant-design/icons";

import {
  Layout,
  Menu,
  Typography,
} from "antd";

import {
  useLocation,
  useNavigate,
} from "react-router-dom";


const {
  Sider,
  Header,
  Content,
} = Layout;


function AppLayout({
  children,
}) {
  const navigate =
    useNavigate();

  const location =
    useLocation();


  const menuItems = [
    {
      key: "/",
      icon:
        <RobotOutlined />,
      label:
        "AI Assistant",
    },
    {
      key: "/knowledge",
      icon:
        <DatabaseOutlined />,
      label:
        "Knowledge Base",
    },
    {
      key: "/evaluation",
      icon:
        <BarChartOutlined />,
      label:
        "PoC Evaluation",
    },
    {
      key: "/status",
      icon:
        <DashboardOutlined />,
      label:
        "System Status",
    },
  ];


  return (
    <Layout
      style={{
        minHeight:
          "100vh",
      }}
    >
      <Sider
        width={230}
        theme="light"
        style={{
          borderRight:
            "1px solid #f0f0f0",
        }}
      >
        <div className="brand">
          <div className="brand-title">
            EdgeTalk Pro
          </div>

          <div className="brand-subtitle">
            Industrial AI Assistant
          </div>
        </div>

        <Menu
          mode="inline"
          selectedKeys={[
            location.pathname,
          ]}
          items={
            menuItems
          }
          onClick={({
            key,
          }) =>
            navigate(key)
          }
        />
      </Sider>

      <Layout>
        <Header
          className="app-header"
        >
          <Typography.Title
            level={4}
            style={{
              margin: 0,
            }}
          >
            工业设备智能维护助手
          </Typography.Title>
        </Header>

        <Content
          className="app-content"
        >
          {children}
        </Content>
      </Layout>
    </Layout>
  );
}


export default AppLayout;
