import type { JobOfferContext, JobOfferGeneratedInfo } from "./types";

type OfferInsightsProps = {
  context: JobOfferContext | null;
  generatedInfo: JobOfferGeneratedInfo | null;
  isExtracting: boolean;
};

export function OfferInsights({
  context,
  generatedInfo,
  isExtracting,
}: OfferInsightsProps) {
  if (!context && !generatedInfo && !isExtracting) return null;

  const contentKey = [
    context?.title,
    context?.company_name,
    generatedInfo?.summary,
    generatedInfo?.keywords.join("|"),
  ].join("");

  return (
    <section
      className={`offer-insights${isExtracting ? " offer-insights--updating" : ""}`}
      aria-label="Información extraída de la oferta"
      aria-busy={isExtracting}
    >
      <div className="offer-insights__status">
        <span className="offer-insights__status-dot" aria-hidden="true" />
        {isExtracting ? "analizando oferta…" : "oferta analizada"}
      </div>

      {isExtracting && !context && !generatedInfo ? (
        <div className="offer-insights__progress" aria-hidden="true">
          <span />
        </div>
      ) : (
        <div className="offer-insights__content" key={contentKey}>
          {context ? (
            <div className="session-card">
              <span>Título de la oferta</span>
              <b>{context.title || "No disponible"}</b>
              <span>Empresa</span>
              <b>{context.company_name || "No disponible"}</b>
            </div>
          ) : null}

          {generatedInfo ? (
            <>
              <div className="session-card session-card--quiet">
                <span>Resumen de la oferta</span>
                <p>{generatedInfo.summary}</p>
              </div>
              <div className="session-card session-card--quiet">
                <span>Keywords</span>
                <ul className="keyword-list" aria-label="Keywords de la oferta">
                  {[...new Set(generatedInfo.keywords)].map((keyword) => (
                    <li key={keyword}>
                      <span className="keyword-list__marker" aria-hidden="true">
                        #
                      </span>
                      {keyword}
                    </li>
                  ))}
                </ul>
              </div>
            </>
          ) : null}
        </div>
      )}
    </section>
  );
}
