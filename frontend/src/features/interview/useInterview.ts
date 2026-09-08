import { useCallback, useEffect, useRef, useState } from "react";
import { replyToInterview, startInterview } from "./api";
import type { ChatMessage, JobOfferContext, JobOfferGeneratedInfo } from "./types";
import { useInterviewWebSocket } from "./useInterviewWs";
import { isValidOfferUrl } from "./validation";

function message(role: ChatMessage["role"], content: string): ChatMessage {
  return { id: crypto.randomUUID(), role, content };
}

export function useInterview() {
  const [sessionId, setSessionId] = useState(() => crypto.randomUUID());
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [jobOfferContext, setJobOfferContext] = useState<JobOfferContext | null>(null);
  const [jobOfferGeneratedInfo, setJobOfferGeneratedInfo] =
    useState<JobOfferGeneratedInfo | null>(null);
  const [isLoading, setLoading] = useState(true);
  const [isAwaitingOfferUrl, setAwaitingOfferUrl] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const generation = useRef(0);

  const onUserTranscript = useCallback((text: string) => {
    setMessages((current) => [...current, message("user", text)]);
  }, []);

  const onAssistantMessage = useCallback((text: string) => {
    setMessages((current) => [...current, message("assistant", text)]);
  }, []);

  const { status: socketStatus, sendVoice } = useInterviewWebSocket(sessionId, {
    onUserTranscript,
    onAssistantMessage,
  });

  useEffect(() => {
    const currentGeneration = ++generation.current;
    setLoading(true);
    setError(null);
    setMessages([]);
    setAwaitingOfferUrl(true);
    startInterview(sessionId)
      .then((response) => {
        if (generation.current === currentGeneration) {
          setMessages([message("assistant", response.assistant_message)]);
        }
      })
      .catch((caught: unknown) => {
        if (generation.current === currentGeneration) {
          setError(
            caught instanceof Error ? caught.message : "No se pudo iniciar JobTalk",
          );
        }
      })
      .finally(() => {
        if (generation.current === currentGeneration) setLoading(false);
      });
  }, [sessionId]);

  const send = useCallback(
    async (content: string) => {
      const cleanContent = content.trim();
      if (!cleanContent || isLoading) return false;
      if (isAwaitingOfferUrl && !isValidOfferUrl(cleanContent)) {
        setError("Introduce una URL válida que empiece por http:// o https://");
        return false;
      }
      const currentGeneration = generation.current;
      setMessages((current) => [...current, message("user", cleanContent)]);
      setLoading(true);
      setError(null);
      try {
        const response = await replyToInterview(sessionId, cleanContent);
        if (generation.current !== currentGeneration) return false;
        setMessages((current) => [
          ...current,
          message("assistant", response.assistant_message),
        ]);
        setJobOfferContext(response.job_offer_context || null);
        setJobOfferGeneratedInfo(response.job_offer_generated_info || null);
        if (isAwaitingOfferUrl) setAwaitingOfferUrl(false);
        return true;
      } catch (caught) {
        if (generation.current !== currentGeneration) return false;
        setError(
          caught instanceof Error ? caught.message : "No se pudo enviar la respuesta",
        );
        return false;
      } finally {
        if (generation.current === currentGeneration) setLoading(false);
      }
    },
    [isAwaitingOfferUrl, isLoading, sessionId],
  );

  const sendVoiceReply = useCallback(
    async (audio: Blob) => {
      if (isLoading) return false;
      const currentGeneration = generation.current;
      setLoading(true);
      setError(null);
      try {
        await sendVoice(audio);
        return generation.current === currentGeneration;
      } catch (caught) {
        if (generation.current !== currentGeneration) return false;
        setError(caught instanceof Error ? caught.message : "No se pudo enviar el audio");
        return false;
      } finally {
        if (generation.current === currentGeneration) setLoading(false);
      }
    },
    [isLoading, sendVoice],
  );

  const resetInterview = () => {
    generation.current += 1;
    setSessionId(crypto.randomUUID());
    setMessages([]);
    setJobOfferContext(null);
    setJobOfferGeneratedInfo(null);
    setAwaitingOfferUrl(true);
    setLoading(true);
    setError(null);
  };

  return {
    sessionId,
    messages,
    jobOfferContext,
    jobOfferGeneratedInfo,
    isLoading,
    isAwaitingOfferUrl,
    error,
    send,
    sendVoice: sendVoiceReply,
    socketStatus,
    reset: () => resetInterview(),
  };
}
