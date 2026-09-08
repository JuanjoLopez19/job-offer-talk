import * as Tooltip from "@radix-ui/react-tooltip";
import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import { Composer } from "./Composer";

describe("Composer", () => {
  afterEach(cleanup);

  it("vacía el campo en cuanto comienza el envío", async () => {
    const user = userEvent.setup();
    let finishSending: ((sent: boolean) => void) | undefined;
    const onSend = vi.fn(
      () =>
        new Promise<boolean>((resolve) => {
          finishSending = resolve;
        }),
    );

    render(
      <Tooltip.Provider>
        <Composer disabled={false} mode="answer" onSend={onSend} onVoice={vi.fn()} />
      </Tooltip.Provider>,
    );

    const input = screen.getByRole("textbox", { name: /tu respuesta/i });
    await user.type(input, "Mi respuesta a la entrevista");
    await user.click(screen.getByRole("button", { name: /enviar/i }));

    expect((input as HTMLTextAreaElement).value).toBe("");
    expect(onSend).toHaveBeenCalledWith("Mi respuesta a la entrevista");
    finishSending?.(true);
  });

  it("exige una URL HTTP válida y oculta la voz durante el primer turno", async () => {
    const user = userEvent.setup();
    const onSend = vi.fn(async () => true);

    render(
      <Tooltip.Provider>
        <Composer disabled={false} mode="offer-url" onSend={onSend} onVoice={vi.fn()} />
      </Tooltip.Provider>,
    );

    const input = screen.getByRole("textbox", {
      name: /url de la oferta de trabajo/i,
    });
    const submit = screen.getByRole("button", { name: /analizar oferta/i });

    expect(input.getAttribute("type")).toBe("url");
    expect(screen.queryByRole("button", { name: /dictar respuesta/i })).toBeNull();
    expect((submit as HTMLButtonElement).disabled).toBe(true);

    await user.type(input, "esto-no-es-una-url");
    expect((submit as HTMLButtonElement).disabled).toBe(true);
    expect(screen.getByText(/introduce una url válida/i)).toBeTruthy();

    await user.clear(input);
    await user.type(input, "ftp://empresa.example/ofertas/backend");
    expect((submit as HTMLButtonElement).disabled).toBe(true);

    await user.clear(input);
    await user.type(input, "https://empresa.example/ofertas/backend");
    expect((submit as HTMLButtonElement).disabled).toBe(false);

    await user.click(submit);
    expect(onSend).toHaveBeenCalledWith("https://empresa.example/ofertas/backend");
  });

  it("detiene la grabación y descarta el audio al desmontarse", async () => {
    const user = userEvent.setup();
    const track = { stop: vi.fn() };
    const stream = { getTracks: () => [track] } as unknown as MediaStream;
    const originalMediaDevices = navigator.mediaDevices;
    const originalMediaRecorder = globalThis.MediaRecorder;

    class FakeMediaRecorder {
      state: RecordingState = "inactive";
      mimeType = "audio/webm";
      listeners = new Map<string, () => void>();

      addEventListener(name: string, listener: () => void) {
        this.listeners.set(name, listener);
      }

      start() {
        this.state = "recording";
      }

      stop() {
        this.state = "inactive";
        this.listeners.get("stop")?.();
      }
    }

    Object.defineProperty(navigator, "mediaDevices", {
      configurable: true,
      value: { getUserMedia: vi.fn(async () => stream) },
    });
    globalThis.MediaRecorder = FakeMediaRecorder as unknown as typeof MediaRecorder;
    const onVoice = vi.fn(async () => true);

    try {
      const { unmount } = render(
        <Tooltip.Provider>
          <Composer disabled={false} mode="answer" onSend={vi.fn()} onVoice={onVoice} />
        </Tooltip.Provider>,
      );
      await user.click(screen.getByRole("button", { name: /dictar respuesta/i }));

      unmount();

      expect(track.stop).toHaveBeenCalled();
      expect(onVoice).not.toHaveBeenCalled();
    } finally {
      Object.defineProperty(navigator, "mediaDevices", {
        configurable: true,
        value: originalMediaDevices,
      });
      globalThis.MediaRecorder = originalMediaRecorder;
    }
  });
});
