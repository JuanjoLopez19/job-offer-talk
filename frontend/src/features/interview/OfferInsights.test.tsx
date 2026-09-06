import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { OfferInsights } from "./OfferInsights";

describe("OfferInsights", () => {
  afterEach(cleanup);

  it("muestra el análisis de forma inline antes de revelar la información", () => {
    const { rerender } = render(
      <OfferInsights context={null} generatedInfo={null} isExtracting />,
    );

    const insights = screen.getByRole("region", {
      name: "Información extraída de la oferta",
    });
    expect(insights.getAttribute("aria-busy")).toBe("true");
    expect(screen.getByText("analizando oferta…")).toBeTruthy();

    rerender(
      <OfferInsights
        context={{ title: "Backend Engineer", company_name: "Acme", url: "https://a.co" }}
        generatedInfo={{ summary: "API y sistemas distribuidos", keywords: ["Python"] }}
        isExtracting={false}
      />,
    );

    expect(insights.getAttribute("aria-busy")).toBe("false");
    expect(screen.getByText("Backend Engineer")).toBeTruthy();
    expect(screen.getByText("API y sistemas distribuidos")).toBeTruthy();
    expect(screen.getByText("Python")).toBeTruthy();
  });
});
