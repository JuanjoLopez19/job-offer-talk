import { useCallback, useEffect, useRef, useState } from "react";

type SocketStatus = "idle" | "open" | "closed" | "error";

type PendingTurn = {
  id: string;
  resolve: () => void;
  reject: (error: Error) => void;
  timeoutId: ReturnType<typeof setTimeout>;
};

type TtsHeader = {
  text: string;
  contentType: string;
  turnId: string | null;
};

type ConversationPayload = {
  event?: string;
  type?: string;
  text?: string;
  message?: string;
  content_type?: string;
  turn_id?: string;
};

const VOICE_TURN_TIMEOUT_MS = 120_000;

export type InterviewSocketHandlers = {
  onUserTranscript?: (text: string) => void;
  onAssistantMessage?: (text: string) => void;
};

function rejectPending(pending: { current: PendingTurn | null }, error: Error) {
  if (!pending.current) return;
  clearTimeout(pending.current.timeoutId);
  pending.current.reject(error);
  pending.current = null;
}

function resolvePending(pending: { current: PendingTurn | null }) {
  if (!pending.current) return;
  clearTimeout(pending.current.timeoutId);
  pending.current.resolve();
  pending.current = null;
}

function toAudioBlob(data: unknown, contentType: string): Blob | null {
  if (data instanceof Blob) return data;
  if (data instanceof ArrayBuffer) return new Blob([data], { type: contentType });
  if (ArrayBuffer.isView(data)) {
    const bytes = new Uint8Array(data.byteLength);
    bytes.set(new Uint8Array(data.buffer, data.byteOffset, data.byteLength));
    return new Blob([bytes], { type: contentType });
  }
  return null;
}

export function useInterviewWebSocket(
  sessionId: string,
  handlers: InterviewSocketHandlers = {},
  isTtsActive = true,
) {
  const socketRef = useRef<WebSocket | null>(null);
  const pendingTurn = useRef<PendingTurn | null>(null);
  const pendingTts = useRef<TtsHeader | null>(null);
  const discardNextBinary = useRef(false);
  const audioPlayer = useRef<HTMLAudioElement | null>(null);
  const audioUrl = useRef<string | null>(null);
  const handlersRef = useRef(handlers);
  const isTtsActiveRef = useRef(isTtsActive);
  const [status, setStatus] = useState<SocketStatus>("idle");
  handlersRef.current = handlers;

  const stopPlayback = useCallback((expectedPlayer?: HTMLAudioElement) => {
    if (expectedPlayer && audioPlayer.current !== expectedPlayer) return;

    const player = audioPlayer.current;
    const url = audioUrl.current;
    audioPlayer.current = null;
    audioUrl.current = null;

    if (player) {
      player.pause();
      player.removeAttribute("src");
    }
    if (url) URL.revokeObjectURL(url);
  }, []);

  const playTtsAudio = useCallback(
    (audio: Blob) => {
      if (typeof Audio === "undefined" || typeof URL.createObjectURL !== "function") {
        return;
      }

      stopPlayback();
      const url = URL.createObjectURL(audio);
      const player = new Audio(url);
      audioPlayer.current = player;
      audioUrl.current = url;

      const release = () => stopPlayback(player);
      player.addEventListener("ended", release, { once: true });
      player.addEventListener("error", release, { once: true });
      void player.play().catch(release);
    },
    [stopPlayback],
  );

  useEffect(() => {
    isTtsActiveRef.current = isTtsActive;
    if (!isTtsActive) stopPlayback();
  }, [isTtsActive, stopPlayback]);

  useEffect(() => {
    setStatus("idle");
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const socket = new WebSocket(
      `${protocol}//${window.location.host}/v1/conversation/${encodeURIComponent(sessionId)}`,
    );
    socket.binaryType = "arraybuffer";
    socketRef.current = socket;

    socket.onopen = () => setStatus("open");
    socket.onerror = () => {
      pendingTts.current = null;
      rejectPending(pendingTurn, new Error("No se pudo enviar el audio"));
      setStatus("error");
    };
    socket.onclose = () => {
      pendingTts.current = null;
      rejectPending(pendingTurn, new Error("Conexión cerrada"));
      socketRef.current = null;
      setStatus("closed");
    };
    socket.onmessage = (event) => {
      if (typeof event.data !== "string") {
        if (discardNextBinary.current) {
          discardNextBinary.current = false;
          return;
        }
        const header = pendingTts.current;
        pendingTts.current = null;
        const audio = header ? toAudioBlob(event.data, header.contentType) : null;
        if (!header || !audio) {
          if (pendingTurn.current) {
            rejectPending(
              pendingTurn,
              new Error("No se pudo leer el audio de respuesta"),
            );
          }
          return;
        }
        if (isTtsActiveRef.current) playTtsAudio(audio);
        if (header.turnId && pendingTurn.current?.id === header.turnId) {
          resolvePending(pendingTurn);
        }
        return;
      }

      let payload: ConversationPayload;
      try {
        payload = JSON.parse(event.data) as ConversationPayload;
      } catch {
        rejectPending(pendingTurn, new Error("No se pudo leer la respuesta de voz"));
        return;
      }

      if (payload.type === "tts_message") {
        if (payload.turn_id && pendingTurn.current?.id !== payload.turn_id) {
          discardNextBinary.current = true;
          return;
        }
        pendingTts.current = {
          text: payload.text ?? "",
          contentType: payload.content_type ?? "audio/wav",
          turnId: payload.turn_id ?? null,
        };
        if (payload.turn_id && payload.text) {
          handlersRef.current.onAssistantMessage?.(payload.text);
        }
        return;
      }

      if (!pendingTurn.current) return;
      if (payload.turn_id !== pendingTurn.current.id) return;

      if (payload.event === "error") {
        rejectPending(
          pendingTurn,
          new Error(payload.message || "No se pudo procesar el mensaje de voz"),
        );
        return;
      }

      if (payload.event === "user_message" && payload.message) {
        handlersRef.current.onUserTranscript?.(payload.message);
        return;
      }

      if (payload.event === "assistant_message") {
        if (payload.message) {
          handlersRef.current.onAssistantMessage?.(payload.message);
          resolvePending(pendingTurn);
          return;
        }
        rejectPending(pendingTurn, new Error("No se recibió la respuesta del asistente"));
      }
    };

    return () => {
      pendingTts.current = null;
      discardNextBinary.current = false;
      rejectPending(pendingTurn, new Error("Conexión cerrada"));
      stopPlayback();
      socket.onopen = null;
      socket.onerror = null;
      socket.onclose = null;
      socket.onmessage = null;
      socket.close();
      socketRef.current = null;
    };
  }, [playTtsAudio, sessionId, stopPlayback]);

  const sendVoice = useCallback(
    async (audio: Blob) => {
      const socket = socketRef.current;
      if (!socket || socket.readyState !== WebSocket.OPEN) {
        throw new Error("Socket no conectado");
      }
      if (pendingTurn.current) {
        throw new Error("Ya hay un mensaje de voz en curso");
      }

      const audioBuffer = await audio.arrayBuffer();
      if (socket !== socketRef.current || socket.readyState !== WebSocket.OPEN) {
        throw new Error("Conexión cerrada");
      }

      const turnId = crypto.randomUUID();
      const turn = new Promise<void>((resolve, reject) => {
        const timeoutId = setTimeout(() => {
          if (pendingTurn.current?.id === turnId) {
            if (pendingTts.current?.turnId === turnId) discardNextBinary.current = true;
            pendingTts.current = null;
            rejectPending(
              pendingTurn,
              new Error("La respuesta de voz ha tardado demasiado"),
            );
          }
        }, VOICE_TURN_TIMEOUT_MS);
        pendingTurn.current = { id: turnId, resolve, reject, timeoutId };
      });

      try {
        socket.send(
          JSON.stringify({
            event: "user_message",
            content_type: audio.type,
            is_tts_active: isTtsActive,
            turn_id: turnId,
          }),
        );
        socket.send(audioBuffer);
      } catch (caught) {
        rejectPending(
          pendingTurn,
          caught instanceof Error ? caught : new Error("No se pudo enviar el audio"),
        );
      }

      return turn;
    },
    [isTtsActive],
  );

  return { status, sendVoice };
}
