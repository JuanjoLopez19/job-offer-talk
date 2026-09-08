import type { GraphResponse } from "./types";

const THREAD_HEADER = "X-Thread-ID";

async function postGraph(
  body: object | string,
  threadId?: string,
): Promise<GraphResponse> {
  const headers = new Headers({ "Content-Type": "application/json" });
  if (threadId) headers.set(THREAD_HEADER, threadId);

  const response = await fetch("/v1/graph/", {
    method: "POST",
    headers,
    body: JSON.stringify(body),
  });

  if (!response.ok) throw new Error("No se pudo continuar la entrevista");
  return response.json() as Promise<GraphResponse>;
}

export function startInterview(sessionId: string) {
  return postGraph({ session_id: sessionId });
}

export function replyToInterview(sessionId: string, message: string) {
  return postGraph(message, sessionId);
}
