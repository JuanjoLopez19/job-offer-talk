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
    expect(
      screen.queryByLabelText(/demostración de una sesión de entrevista/i),
    ).toBeNull();
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

    const demoVideo = screen.getByLabelText(/demostración de una sesión de entrevista/i);
    const demoSource = demoVideo.querySelector("source");
    expect(demoSource?.getAttribute("src")).toBe(
      "https://bucket.jjlopez.dev/videos/job_talk_demo.mp4",
    );
    expect(demoSource?.getAttribute("type")).toBe("video/mp4");
    expect(demoVideo.hasAttribute("autoplay")).toBe(true);
    expect(demoVideo.hasAttribute("controls")).toBe(true);
    expect(demoVideo.hasAttribute("loop")).toBe(true);
    expect((demoVideo as HTMLVideoElement).muted).toBe(true);
  });
});

import * as Tooltip from "@radix-ui/react-tooltip";
