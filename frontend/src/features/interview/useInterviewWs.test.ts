import { act, cleanup, renderHook } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { useInterviewWebSocket } from "./useInterviewWs";

class MockWebSocket {
  static OPEN = 1;
  static instances: MockWebSocket[] = [];

  readonly url: string;
  readyState = 0;
  sent: unknown[] = [];
  onopen: (() => void) | null = null;
  onclose: (() => void) | null = null;
  onerror: (() => void) | null = null;
  onmessage: ((event: { data: unknown }) => void) | null = null;

  constructor(url: string) {
    this.url = url;
    MockWebSocket.instances.push(this);
  }

  send(data: unknown) {
    this.sent.push(data);
  }

  close() {
    this.readyState = 3;
    this.onclose?.();
  }

  open() {
    this.readyState = MockWebSocket.OPEN;
    this.onopen?.();
  }

  emit(data: unknown) {
    this.onmessage?.({ data });
  }
}

const originalWebSocket = globalThis.WebSocket;
const originalAudio = globalThis.Audio;
const originalCreateObjectUrl = URL.createObjectURL;
const originalRevokeObjectUrl = URL.revokeObjectURL;

class MockAudio {
  static instances: MockAudio[] = [];

  src: string;
  pause = vi.fn();
  play = vi.fn(async () => undefined);
  removeAttribute = vi.fn((name: string) => {
    if (name === "src") this.src = "";
  });

  constructor(src: string) {
    this.src = src;
    MockAudio.instances.push(this);
  }

  addEventListener() {}
}

describe("useInterviewWebSocket", () => {
  beforeEach(() => {
    MockWebSocket.instances = [];
    MockAudio.instances = [];
    globalThis.WebSocket = MockWebSocket as unknown as typeof WebSocket;
    globalThis.Audio = MockAudio as unknown as typeof Audio;
    Object.defineProperty(URL, "createObjectURL", {
      configurable: true,
      value: vi.fn(() => "blob:tts-audio"),
    });
    Object.defineProperty(URL, "revokeObjectURL", {
      configurable: true,
      value: vi.fn(),
    });
  });

  afterEach(() => {
    cleanup();
    globalThis.WebSocket = originalWebSocket;
    globalThis.Audio = originalAudio;
    Object.defineProperty(URL, "createObjectURL", {
      configurable: true,
      value: originalCreateObjectUrl,
    });
    Object.defineProperty(URL, "revokeObjectURL", {
      configurable: true,
      value: originalRevokeObjectUrl,
    });
    vi.useRealTimers();
  });

  it("abre un socket por sesión y completa el turno de voz sin cerrarlo", async () => {
    const onUserTranscript = vi.fn();
    const onAssistantMessage = vi.fn();
    const { result } = renderHook(() =>
      useInterviewWebSocket("session-1", { onUserTranscript, onAssistantMessage }),
    );
    const socket = MockWebSocket.instances.at(-1);
    expect(socket?.url).toContain("/v1/conversation/session-1");

    act(() => socket?.open());
    expect(result.current.status).toBe("open");

    const audio = new Blob(["audio"], { type: "audio/webm" });
    const turn = result.current.sendVoice(audio);
    await act(async () => {
      await Promise.resolve();
    });

    const metadata = JSON.parse(String(socket?.sent[0])) as { turn_id: string };
    expect(metadata).toMatchObject({
      event: "user_message",
      content_type: "audio/webm",
      is_tts_active: true,
    });
    expect(socket?.sent[1]).toBeInstanceOf(ArrayBuffer);

    act(() =>
      socket?.emit(
        JSON.stringify({
          event: "user_message",
          message: "Hola desde voz",
          turn_id: metadata.turn_id,
        }),
      ),
    );
    act(() =>
      socket?.emit(
        JSON.stringify({
          type: "tts_message",
          text: "Pregunta del asistente",
          content_type: "audio/wav",
          turn_id: metadata.turn_id,
        }),
      ),
    );
    act(() => socket?.emit(new ArrayBuffer(8)));

    await expect(turn).resolves.toBeUndefined();
    expect(onUserTranscript).toHaveBeenCalledWith("Hola desde voz");
    expect(onAssistantMessage).toHaveBeenCalledWith("Pregunta del asistente");
    expect(socket?.readyState).toBe(MockWebSocket.OPEN);
    expect(MockWebSocket.instances).toHaveLength(1);
  });

  it("detiene el audio activo al cambiar de sesión", async () => {
    const { result, rerender } = renderHook(
      ({ sessionId }) => useInterviewWebSocket(sessionId),
      { initialProps: { sessionId: "session-1" } },
    );
    const socket = MockWebSocket.instances.at(-1);
    act(() => socket?.open());

    const turn = result.current.sendVoice(new Blob(["audio"], { type: "audio/webm" }));
    await act(async () => Promise.resolve());
    const metadata = JSON.parse(String(socket?.sent[0])) as { turn_id: string };
    act(() =>
      socket?.emit(
        JSON.stringify({
          type: "tts_message",
          text: "Respuesta",
          content_type: "audio/wav",
          turn_id: metadata.turn_id,
        }),
      ),
    );
    act(() => socket?.emit(new ArrayBuffer(8)));
    await expect(turn).resolves.toBeUndefined();

    const player = MockAudio.instances.at(-1);
    rerender({ sessionId: "session-2" });

    expect(player?.pause).toHaveBeenCalledOnce();
    expect(player?.removeAttribute).toHaveBeenCalledWith("src");
    expect(URL.revokeObjectURL).toHaveBeenCalledWith("blob:tts-audio");
  });

  it("detiene el audio recibido por HTTP al abandonar la entrevista", () => {
    const { unmount } = renderHook(() => useInterviewWebSocket("session-1"));
    const socket = MockWebSocket.instances.at(-1);
    act(() => socket?.open());
    act(() =>
      socket?.emit(
        JSON.stringify({
          type: "tts_message",
          text: "Respuesta de texto",
          content_type: "audio/wav",
        }),
      ),
    );
    act(() => socket?.emit(new ArrayBuffer(8)));

    const player = MockAudio.instances.at(-1);
    unmount();

    expect(player?.pause).toHaveBeenCalledOnce();
    expect(URL.revokeObjectURL).toHaveBeenCalledWith("blob:tts-audio");
  });

  it("detiene el audio activo y envía la preferencia al desactivar TTS", async () => {
    const { result, rerender } = renderHook(
      ({ isTtsActive }) => useInterviewWebSocket("session-1", {}, isTtsActive),
      { initialProps: { isTtsActive: true } },
    );
    const socket = MockWebSocket.instances.at(-1);
    act(() => socket?.open());
    act(() =>
      socket?.emit(
        JSON.stringify({
          type: "tts_message",
          text: "Respuesta",
          content_type: "audio/wav",
        }),
      ),
    );
    act(() => socket?.emit(new ArrayBuffer(8)));

    const player = MockAudio.instances.at(-1);
    rerender({ isTtsActive: false });
    expect(player?.pause).toHaveBeenCalledOnce();

    const turn = result.current.sendVoice(new Blob(["audio"], { type: "audio/webm" }));
    await act(async () => Promise.resolve());
    const metadata = JSON.parse(String(socket?.sent[0])) as {
      is_tts_active: boolean;
      turn_id: string;
    };
    expect(metadata.is_tts_active).toBe(false);

    act(() =>
      socket?.emit(
        JSON.stringify({
          event: "assistant_message",
          message: "Respuesta sin audio",
          turn_id: metadata.turn_id,
        }),
      ),
    );
    await expect(turn).resolves.toBeUndefined();
  });

  it("cancela el turno cuando el servidor tarda demasiado", async () => {
    vi.useFakeTimers();
    const { result } = renderHook(() => useInterviewWebSocket("session-1"));
    const socket = MockWebSocket.instances.at(-1);
    act(() => socket?.open());

    const turn = result.current.sendVoice(new Blob(["audio"], { type: "audio/webm" }));
    const rejection = expect(turn).rejects.toThrow(
      "La respuesta de voz ha tardado demasiado",
    );
    await act(async () => Promise.resolve());
    await act(async () => vi.advanceTimersByTimeAsync(120_000));

    await rejection;
  });

  it("cancela un turno de voz pendiente al cambiar de sesión", async () => {
    const { result, rerender } = renderHook(
      ({ sessionId }) => useInterviewWebSocket(sessionId),
      { initialProps: { sessionId: "session-1" } },
    );
    const firstSocket = MockWebSocket.instances.at(-1);
    act(() => firstSocket?.open());

    const turn = result.current.sendVoice(new Blob(["audio"]));
    await act(async () => {
      await Promise.resolve();
    });

    rerender({ sessionId: "session-2" });

    await expect(turn).rejects.toThrow("Conexión cerrada");
    expect(MockWebSocket.instances.at(-1)?.url).toContain("/v1/conversation/session-2");
  });
});
