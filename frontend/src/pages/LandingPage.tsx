import { ArrowRight } from "lucide-react";
import { Link } from "react-router-dom";
import { SiteHeader } from "../components/layout/SiteHeader";

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
            <Link className="button button--primary" to="/entrevista">
              Abrir entrevista <ArrowRight aria-hidden="true" />
            </Link>
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
          <Link className="button button--primary" to="/entrevista">
            Empezar práctica
          </Link>
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
