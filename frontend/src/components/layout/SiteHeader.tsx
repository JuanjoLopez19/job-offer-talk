import { Link } from "react-router-dom";
import { ThemeToggle } from "../ui/ThemeToggle";
import { InterviewCta } from "./InterviewCta";

export function SiteHeader() {
  return (
    <header className="site-header">
      <Link className="wordmark" to="/" aria-label="JobTalk, inicio">
        <img
          className="brand-icon"
          src={`${import.meta.env.BASE_URL}jobtalk-icon.webp`}
          alt=""
          aria-hidden="true"
        />
        <span>[ JobTalk ]</span>
      </Link>
      <nav className="site-nav" aria-label="Navegación principal">
        <a href="#producto">Producto</a>
        <a href="#flujo">Flujo</a>
        <a href="#demo">Demo</a>
        <a href="#voz">Voz</a>
      </nav>
      <div className="site-header__actions">
        <ThemeToggle />
        <InterviewCta className="button button--primary">Probar ahora</InterviewCta>
      </div>
    </header>
  );
}
