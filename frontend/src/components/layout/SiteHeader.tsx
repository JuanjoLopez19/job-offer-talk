import { Link } from "react-router-dom";
import { ThemeToggle } from "../ui/ThemeToggle";

export function SiteHeader() {
  return (
    <header className="site-header">
      <Link className="wordmark" to="/" aria-label="JobTalk, inicio">
        [ JobTalk ]
      </Link>
      <nav className="site-nav" aria-label="Navegación principal">
        <a href="#producto">Producto</a>
        <a href="#flujo">Flujo</a>
        <a href="#voz">Voz</a>
      </nav>
      <div className="site-header__actions">
        <ThemeToggle />
        <Link className="button button--primary" to="/interview">
          Probar ahora
        </Link>
      </div>
    </header>
  );
}
