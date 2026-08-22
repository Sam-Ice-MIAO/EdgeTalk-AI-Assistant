import {
  BrowserRouter,
  Route,
  Routes,
} from "react-router-dom";

import AppLayout from "./components/AppLayout";

import ChatPage from "./pages/ChatPage";
import KnowledgePage from "./pages/KnowledgePage";
import StatusPage from "./pages/StatusPage";

function App() {
  return (
    <BrowserRouter>
      <AppLayout>
        <Routes>
          <Route
            path="/"
            element={<ChatPage />}
          />

          <Route
            path="/knowledge"
            element={<KnowledgePage />}
          />

          <Route
            path="/status"
            element={<StatusPage />}
          />
        </Routes>
      </AppLayout>
    </BrowserRouter>
  );
}

export default App;
