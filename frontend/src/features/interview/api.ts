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

export function transcribeAudio(sessionId: string, audio: Blob): Promise<string> {
  return new Promise((resolve, reject) => {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const socket = new WebSocket(
      `${protocol}//${window.location.host}/v1/conversation/${encodeURIComponent(sessionId)}`,
    );

    socket.addEventListener("open", async () => {
      socket.send(JSON.stringify({ event: "user_message", content_type: audio.type }));
      socket.send(await audio.arrayBuffer());
    });
    socket.addEventListener("message", (event) => {
      if (typeof event.data !== "string") return;
      const payload = JSON.parse(event.data) as { message?: string };
      socket.close();
      if (payload.message) resolve(payload.message);
      else reject(new Error("No se recibió una transcripción"));
    });
    socket.addEventListener("error", () =>
      reject(new Error("No se pudo transcribir el audio")),
    );
  });
}
