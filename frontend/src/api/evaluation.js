import apiClient from "./client";


export async function getLatestEvaluation() {
  const response =
    await apiClient.get(
      "/evaluation/latest"
    );

  return response.data;
}


export async function getEvaluationReport() {
  const response =
    await apiClient.get(
      "/evaluation/report"
    );

  return response.data;
}


export async function downloadEvaluationReport() {
  const response =
    await apiClient.get(
      "/evaluation/report/download",
      {
        responseType: "blob",
      }
    );

  const blob = new Blob(
    [response.data],
    {
      type:
        "text/markdown;charset=utf-8",
    }
  );

  const url =
    window.URL.createObjectURL(
      blob
    );

  const link =
    document.createElement(
      "a"
    );

  link.href = url;

  link.download =
    "EdgeTalk-Pro-PoC-Report.md";

  document.body.appendChild(
    link
  );

  link.click();

  document.body.removeChild(
    link
  );

  window.URL.revokeObjectURL(
    url
  );
}
