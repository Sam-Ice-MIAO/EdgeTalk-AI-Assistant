import apiClient from "./client";

export async function getLatestEvaluation() {
  const response = await apiClient.get(
    "/evaluation/latest"
  );

  return response.data;
}
