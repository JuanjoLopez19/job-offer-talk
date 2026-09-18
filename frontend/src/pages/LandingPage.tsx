import { ArrowRight } from "lucide-react";
import { Link } from "react-router-dom";
import { InterviewCta } from "../components/layout/InterviewCta";
import { SiteHeader } from "../components/layout/SiteHeader";
import { isGitHubPages } from "../config/environment";

const DEMO_VIDEO_URL = "https://bucket.jjlopez.dev/videos/job_talk_demo.mp4";

const benefits = [
  [
    "Extrae la oferta",
    "Convierte una URL en responsabilidades, requisitos y tecnologías clave.",
  ],
  [
    "Genera preguntas",
    "Prepara una entrevista alineada con el rol, no un cuestionario genérico.",
  ],
  [
    "Mantiene el turno",
    "Conserva el contexto necesario mientras dura la práctica activa.",
  ],
  ["Integra voz", "Te permite responder hablando o escribiendo, sin adjuntar archivos."],
];

export function LandingPage() {
  const showDemoVideo = isGitHubPages();

  return (
    <div className="landing">
      <SiteHeader />
      <main>
        <section className="hero" aria-labelledby="hero-title">
          <h1 id="hero-title">Practica con un asistente que entiende la oferta</h1>
          <p>
            Pega una vacante y entra en una simulación única con preguntas relevantes,
            feedback accionable y soporte de voz.
          </p>
          <div className="hero__actions">
            <InterviewCta className="button button--primary">
              Abrir entrevista <ArrowRight aria-hidden="true" />
            </InterviewCta>
            <a className="button button--secondary" href="#flujo">
              Ver cómo funciona
            </a>
          </div>
          <div className="terminal" role="img" aria-label="Vista previa de JobTalk">
            <strong>JOBTALK</strong>
            <span>[ entrevista guiada ]</span>
            <div className="terminal__prompt">
              <p>| Analiza esta oferta y prepara una entrevista técnica</p>
              <small>
                modo: sesión temporal · voz: disponible · sin historial ni registros
              </small>
            </div>
            <div className="terminal__facts">
              <p>
                <b>[+] oferta</b>
                <span>requisitos y stack detectados</span>
              </p>
              <p>
                <b>[+] preguntas</b>
                <span>adaptadas al puesto</span>
              </p>
              <p>
                <b>[x] checkpoints</b>
                <span>reanuda el turno exacto</span>
              </p>
            </div>
          </div>
        </section>

        {showDemoVideo && (
          <section className="demo-section" id="demo" aria-labelledby="demo-title">
            <div className="demo-section__meta">
              <span className="demo-section__eyebrow">Deployment preview</span>
            </div>
            <h2 id="demo-title">Demo interactiva de JobTalk</h2>
            <p id="demo-description">
              Mira cómo JobTalk convierte una oferta en una entrevista guiada.
            </p>
            <div className="demo-section__player">
              <video
                aria-label="Demostración de una sesión de entrevista en JobTalk"
                aria-describedby="demo-description"
                autoPlay
                controls
                loop
                muted
                playsInline
                preload="metadata"
              >
                <source src={DEMO_VIDEO_URL} type="video/mp4" />
                Tu navegador no permite reproducir este vídeo.
              </video>
            </div>
          </section>
        )}

        <section
          className="content-section"
          id="producto"
          aria-labelledby="product-title"
        >
          <h2 id="product-title">[+] Qué hace JobTalk</h2>
          <div className="benefit-list">
            {benefits.map(([title, description]) => (
              <article key={title}>
                <b>[+] {title}</b>
                <p>{description}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="content-section" id="flujo" aria-labelledby="flow-title">
          <h2 id="flow-title">[+] El flujo de una sesión</h2>
          <ol className="flow-grid">
            <li>
              <span>[01]</span>Pega la URL de la oferta
            </li>
            <li>
              <span>[02]</span>Revisa los datos extraídos
            </li>
            <li>
              <span>[03]</span>Responde pregunta a pregunta
            </li>
            <li>
              <span>[04]</span>Cierra con feedback accionable
            </li>
          </ol>
        </section>

        <section className="voice-cta" id="voz">
          <div>
            <span>[+] voz opcional</span>
            <h2>Escribe cuando quieras. Habla cuando te resulte natural.</h2>
          </div>
          <InterviewCta className="button button--primary">Empezar práctica</InterviewCta>
        </section>
      </main>
      <footer>
        <span>©2026 JobTalk v1.0.0</span>
        <span>
          <Link
            to="https://portfolio.jjlopez.dev?utm_source=jobtalk&utm_medium=footer"
            target="_blank"
            rel="noopener"
          >
            Made by <b>@JuanjoLopez19</b>
          </Link>
        </span>
      </footer>
    </div>
  );
}
