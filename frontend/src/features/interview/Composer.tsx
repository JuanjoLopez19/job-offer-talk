import * as Tooltip from "@radix-ui/react-tooltip";
import { Mic, Send, Square } from "lucide-react";
import { type FormEvent, useEffect, useRef, useState } from "react";
import { Button } from "../../components/ui/Button";
import { isValidOfferUrl } from "./validation";

type ComposerProps = {
  disabled: boolean;
  voiceDisabled?: boolean;
  mode: "offer-url" | "answer";
  onSend: (content: string) => Promise<boolean>;
  onVoice: (audio: Blob) => Promise<boolean>;
};

export function Composer({
  disabled,
  voiceDisabled = false,
  mode,
  onSend,
  onVoice,
}: ComposerProps) {
  const [value, setValue] = useState("");
  const [isRecording, setRecording] = useState(false);
  const [isTranscribing, setTranscribing] = useState(false);
  const [voiceError, setVoiceError] = useState<string | null>(null);
  const recorder = useRef<MediaRecorder | null>(null);
  const mediaStream = useRef<MediaStream | null>(null);
  const chunks = useRef<Blob[]>([]);
  const mounted = useRef(true);
  const discardRecording = useRef(false);

  useEffect(() => {
    mounted.current = true;
    return () => {
      mounted.current = false;
      discardRecording.current = true;
      if (recorder.current?.state === "recording") recorder.current.stop();
      for (const track of mediaStream.current?.getTracks() ?? []) track.stop();
      recorder.current = null;
      mediaStream.current = null;
    };
  }, []);

  const isOfferUrlMode = mode === "offer-url";
  const hasValidValue = isOfferUrlMode ? isValidOfferUrl(value) : Boolean(value.trim());
  const urlError =
    isOfferUrlMode && value.length > 0 && !hasValidValue
      ? "Introduce una URL válida que empiece por http:// o https://"
      : null;

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!hasValidValue) return;
    const submittedValue = value;
    setValue("");
    await onSend(submittedValue);
  }

  async function toggleRecording() {
    setVoiceError(null);
    if (recorder.current?.state === "recording") {
      recorder.current.stop();
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      if (!mounted.current) {
        for (const track of stream.getTracks()) track.stop();
        return;
      }
      const mediaRecorder = new MediaRecorder(stream);
      recorder.current = mediaRecorder;
      mediaStream.current = stream;
      discardRecording.current = false;
      chunks.current = [];
      mediaRecorder.addEventListener("dataavailable", (event) =>
        chunks.current.push(event.data),
      );
      mediaRecorder.addEventListener("stop", async () => {
        for (const track of stream.getTracks()) track.stop();
        if (recorder.current === mediaRecorder) recorder.current = null;
        if (mediaStream.current === stream) mediaStream.current = null;
        if (discardRecording.current || !mounted.current) return;

        setRecording(false);
        setTranscribing(true);
        try {
          await onVoice(new Blob(chunks.current, { type: mediaRecorder.mimeType }));
        } catch (caught) {
          if (mounted.current) {
            setVoiceError(
              caught instanceof Error ? caught.message : "No se pudo usar el micrófono",
            );
          }
        } finally {
          if (mounted.current) setTranscribing(false);
        }
      });
      mediaRecorder.start();
      setRecording(true);
    } catch {
      if (mounted.current) {
        setVoiceError("Permite el acceso al micrófono para dictar tu respuesta");
      }
    }
  }

  const micLabel = isRecording ? "Detener grabación" : "Dictar respuesta";
  return (
    <form className="composer" onSubmit={submit}>
      <div className="composer__row">
        <label className="sr-only" htmlFor="interview-input">
          {isOfferUrlMode ? "URL de la oferta de trabajo" : "Tu respuesta"}
        </label>
        {isOfferUrlMode ? (
          <input
            id="interview-input"
            name="offer-url"
            type="url"
            inputMode="url"
            autoComplete="url"
            spellCheck={false}
            value={value}
            onChange={(event) => setValue(event.target.value)}
            placeholder="https://empresa.com/ofertas/puesto"
            aria-describedby="composer-help"
            aria-invalid={Boolean(urlError)}
            disabled={disabled}
            required
          />
        ) : (
          <textarea
            id="interview-input"
            name="answer"
            rows={1}
            value={value}
            onChange={(event) => setValue(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                event.currentTarget.form?.requestSubmit();
              }
            }}
            placeholder="Escribe tu respuesta o pulsa el micrófono para hablar…"
            aria-describedby="composer-help"
            disabled={disabled}
          />
        )}
        {!isOfferUrlMode ? (
          <Tooltip.Root>
            <Tooltip.Trigger asChild>
              <Button
                className={isRecording ? "button--recording" : ""}
                variant="icon"
                type="button"
                onClick={toggleRecording}
                aria-label={micLabel}
                disabled={
                  isRecording ? false : disabled || voiceDisabled || isTranscribing
                }
              >
                {isRecording ? <Square aria-hidden="true" /> : <Mic aria-hidden="true" />}
              </Button>
            </Tooltip.Trigger>
            <Tooltip.Portal>
              <Tooltip.Content className="tooltip" sideOffset={8}>
                {micLabel}
                <Tooltip.Arrow className="tooltip__arrow" />
              </Tooltip.Content>
            </Tooltip.Portal>
          </Tooltip.Root>
        ) : null}
        <Button type="submit" disabled={disabled || !hasValidValue}>
          <span>{isOfferUrlMode ? "Analizar oferta" : "Enviar"}</span>
          <Send aria-hidden="true" />
        </Button>
      </div>
      <p
        id="composer-help"
        className={
          voiceError || urlError
            ? "composer__help composer__help--error"
            : "composer__help"
        }
      >
        {urlError ??
          voiceError ??
          (isOfferUrlMode
            ? "Pega la URL completa de la oferta. La voz estará disponible después."
            : "Solo texto y voz. No se guardará un historial en este dispositivo.")}
      </p>
    </form>
  );
}
