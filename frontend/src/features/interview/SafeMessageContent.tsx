import DOMPurify from "dompurify";
import { useMemo } from "react";

const SAFE_FORMATTING_TAGS = [
  "b",
  "strong",
  "em",
  "i",
  "u",
  "s",
  "br",
  "p",
  "ul",
  "ol",
  "li",
  "blockquote",
  "code",
  "pre",
];

export function SafeMessageContent({ content }: { content: string }) {
  const sanitizedContent = useMemo(
    () =>
      DOMPurify.sanitize(content, {
        ALLOWED_TAGS: SAFE_FORMATTING_TAGS,
        ALLOWED_ATTR: [],
        ALLOW_ARIA_ATTR: false,
        ALLOW_DATA_ATTR: false,
      }),
    [content],
  );

  return (
    <div
      className="message__content"
      // biome-ignore lint/security/noDangerouslySetInnerHtml: DOMPurify sanitizes a strict formatting-only allowlist immediately before this HTML sink.
      dangerouslySetInnerHTML={{ __html: sanitizedContent }}
    />
  );
}
