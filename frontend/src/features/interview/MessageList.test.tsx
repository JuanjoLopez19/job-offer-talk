import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { MessageList } from "./MessageList";

describe("MessageList", () => {
  afterEach(() => {
    cleanup();
    Reflect.deleteProperty(HTMLElement.prototype, "scrollTo");
  });

  it("desplaza únicamente el contenedor de mensajes", () => {
    const scrollTo = vi.fn();
    Object.defineProperty(HTMLElement.prototype, "scrollTo", {
      configurable: true,
      value: scrollTo,
    });

    const { rerender } = render(<MessageList messages={[]} isLoading />);

    expect(() =>
      rerender(
        <MessageList
          messages={[{ id: "message-1", role: "assistant", content: "Hola" }]}
          isLoading={false}
        />,
      ),
    ).not.toThrow();
    expect(scrollTo).toHaveBeenCalledTimes(2);
    expect(scrollTo).toHaveBeenLastCalledWith({ top: 0, behavior: "smooth" });
  });

  it("renderiza formato permitido y elimina contenido ejecutable", () => {
    Object.defineProperty(HTMLElement.prototype, "scrollTo", {
      configurable: true,
      value: vi.fn(),
    });

    const { container } = render(
      <MessageList
        messages={[
          {
            id: "message-1",
            role: "assistant",
            content:
              '<b onclick="alert(1)">JobTalk</b><img src=x onerror="alert(2)"><script>alert(3)</script>',
          },
        ]}
        isLoading={false}
      />,
    );

    const formattedText = screen.getByText("JobTalk");
    expect(formattedText.tagName).toBe("B");
    expect(formattedText.getAttributeNames()).toEqual([]);
    expect(container.querySelector("img")).toBeNull();
    expect(container.querySelector("script")).toBeNull();
    expect(container.innerHTML).not.toContain("onclick");
    expect(container.innerHTML).not.toContain("onerror");
  });
});
