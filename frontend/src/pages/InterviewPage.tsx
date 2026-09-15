import { Volume2, VolumeX } from "lucide-react";
import { Link } from "react-router-dom";
import { ThemeToggle } from "../components/ui/ThemeToggle";
import { Composer } from "../features/interview/Composer";
import { MessageList } from "../features/interview/MessageList";
import { OfferInsights } from "../features/interview/OfferInsights";
import { ResetSessionDialog } from "../features/interview/ResetSessionDialog";
import { useInterview } from "../features/interview/useInterview";

export function InterviewPage() {
  const interview = useInterview();
  const isExtractingOffer =
    interview.isLoading &&
    interview.isAwaitingOfferUrl &&
    interview.messages.some((item) => item.role === "user");

  return (
    <div className="interview-page">
      <header className="interview-header">
        <Link className="wordmark" to="/">
          <img
            className="brand-icon"
            src={`${import.meta.env.BASE_URL}jobtalk-icon.png`}
            alt=""
            aria-hidden="true"
          />
          <span>[ JobTalk / entrevista ]</span>
        </Link>
        <div className="interview-header__actions">
          <button
            className="tts-toggle"
            type="button"
            role="switch"
            aria-checked={interview.isTtsActive}
            onClick={interview.toggleTts}
          >
            {interview.isTtsActive ? (
              <Volume2 aria-hidden="true" />
            ) : (
              <VolumeX aria-hidden="true" />
            )}
            <span>TTS</span>
            <span className="tts-toggle__track" aria-hidden="true">
              <span className="tts-toggle__thumb" />
            </span>
            <span className="sr-only">
              {interview.isTtsActive
                ? "Desactivar voz del asistente"
                : "Activar voz del asistente"}
            </span>
          </button>
          <ThemeToggle />
        </div>
      </header>
      <div className="interview-layout">
        <aside className="session-panel">
          <ResetSessionDialog onReset={interview.reset} />
          <h2>sesión actual</h2>
          <p>
            Cada visita inicia una práctica independiente. No mostramos conversaciones
            anteriores.
          </p>
          <OfferInsights
            context={interview.jobOfferContext}
            generatedInfo={interview.jobOfferGeneratedInfo}
            isExtracting={isExtractingOffer}
          />
        </aside>
        <main className="conversation">
          <header className="conversation__header">
            <h1>Prepara tu próxima entrevista</h1>
            <p>
              {interview.jobOfferContext?.url && (
                <Link
                  to={interview.jobOfferContext.url}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  fuente: {interview.jobOfferContext.url}
                </Link>
              )}
            </p>
          </header>
          {interview.error ? (
            <div className="error-banner" role="alert">
              [!] {interview.error}
            </div>
          ) : null}
          <MessageList messages={interview.messages} isLoading={interview.isLoading} />
          <Composer
            key={interview.sessionId}
            disabled={interview.isLoading}
            voiceDisabled={interview.socketStatus !== "open"}
            mode={interview.isAwaitingOfferUrl ? "offer-url" : "answer"}
            onSend={interview.send}
            onVoice={interview.sendVoice}
          />
        </main>
      </div>
    </div>
  );
}
