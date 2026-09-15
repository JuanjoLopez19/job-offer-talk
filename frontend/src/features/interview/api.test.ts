import { afterEach, describe, expect, it, vi } from "vitest";
import { replyToInterview, startInterview } from "./api";

function successfulFetch() {
  return vi.fn((_input: RequestInfo | URL, _init?: RequestInit) =>
    Promise.resolve(
      new Response(JSON.stringify({ assistant_message: "Hola" }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    ),
  );
}

describe("interview API", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("inicia la entrevista con TTS activo", async () => {
    const fetchMock = successfulFetch();
    vi.stubGlobal("fetch", fetchMock);

    await startInterview("session-1", true);

    const init = fetchMock.mock.calls[0]?.[1];
    expect(JSON.parse(String(init?.body))).toEqual({
      session_id: "session-1",
      is_tts_active: true,
    });
  });

  it("envía la preferencia TTS en cada respuesta de texto", async () => {
    const fetchMock = successfulFetch();
    vi.stubGlobal("fetch", fetchMock);

    await replyToInterview("session-1", "Mi respuesta", false);

    const init = fetchMock.mock.calls[0]?.[1];
    expect(JSON.parse(String(init?.body))).toEqual({
      session_id: "session-1",
      user_input: "Mi respuesta",
      is_tts_active: false,
    });
    expect(new Headers(init?.headers).get("X-Thread-ID")).toBe("session-1");
  });
});
