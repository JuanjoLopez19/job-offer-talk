import * as Tooltip from "@radix-ui/react-tooltip";
import { Navigate, Route, Routes } from "react-router-dom";
import { ThemeProvider } from "./features/theme/ThemeProvider";
import { InterviewPage } from "./pages/InterviewPage";
import { LandingPage } from "./pages/LandingPage";

export function App() {
  return (
    <ThemeProvider>
      <Tooltip.Provider delayDuration={250}>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/interview" element={<InterviewPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Tooltip.Provider>
    </ThemeProvider>
  );
}
