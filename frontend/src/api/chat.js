import apiClient from "./client";

export async function sendAgentMessage(text, sessionId) {
  const response = await apiClient.post("/agent-chat", {
    text,
    session_id: sessionId,
  });

  return response.data;
}
