import { cleanup, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";
import { ThemeProvider } from "../features/theme/ThemeProvider";
import { LandingPage } from "./LandingPage";

describe("LandingPage", () => {
  afterEach(() => {
    cleanup();
    vi.unstubAllEnvs();
  });

  it("ofrece acceso directo a la entrevista", () => {
    render(
      <ThemeProvider>
        <Tooltip.Provider>
          <MemoryRouter>
            <LandingPage />
          </MemoryRouter>
        </Tooltip.Provider>
      </ThemeProvider>,
    );
    expect(screen.getByRole("heading", { level: 1 }).textContent).toContain("Practica");
    expect(
      screen.getByRole("link", { name: /abrir entrevista/i }).getAttribute("href"),
    ).toBe("/interview");
  });

  it("redirige las llamadas a la acción al repositorio en GitHub Pages", () => {
    vi.stubEnv("VITE_GITHUB_PAGES", "true");

    render(
      <ThemeProvider>
        <Tooltip.Provider>
          <MemoryRouter>
            <LandingPage />
          </MemoryRouter>
        </Tooltip.Provider>
      </ThemeProvider>,
    );

    for (const name of [/probar ahora/i, /abrir entrevista/i, /empezar práctica/i]) {
      expect(screen.getByRole("link", { name }).getAttribute("href")).toBe(
        "https://github.com/JuanjoLopez19/job-offer-talk",
      );
    }
  });
});

import * as Tooltip from "@radix-ui/react-tooltip";
