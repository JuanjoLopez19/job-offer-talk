import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";
import { ThemeProvider } from "../features/theme/ThemeProvider";
import { LandingPage } from "./LandingPage";

describe("LandingPage", () => {
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
});

import * as Tooltip from "@radix-ui/react-tooltip";
