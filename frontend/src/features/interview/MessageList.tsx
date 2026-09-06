import { useEffect, useRef } from "react";
import { SafeMessageContent } from "./SafeMessageContent";
import type { ChatMessage } from "./types";

type MessageListProps = { messages: ChatMessage[]; isLoading: boolean };

export function MessageList({ messages, isLoading }: MessageListProps) {
  const messagesRef = useRef<HTMLElement>(null);

  useEffect(() => {
    const container = messagesRef.current;
    container?.scrollTo({ top: container.scrollHeight, behavior: "smooth" });
  });

  return (
    <section
      ref={messagesRef}
      className="messages"
      aria-label="Conversación"
      aria-live="polite"
    >
      {messages.map((item) => (
        <article className={`message message--${item.role}`} key={item.id}>
          <span>{item.role === "assistant" ? "Agente de JobTalk" : "tú"}</span>
          <SafeMessageContent content={item.content} />
        </article>
      ))}
      {isLoading && messages.length > 0 ? (
        <div className="typing" role="status">
          <span /> <span /> <span />
          <span className="sr-only">JobTalk está preparando una respuesta</span>
        </div>
      ) : null}
    </section>
  );
}
