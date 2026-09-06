import * as Tooltip from "@radix-ui/react-tooltip";
import { Moon, Sun } from "lucide-react";
import { useTheme } from "../../features/theme/ThemeProvider";
import { Button } from "./Button";

export function ThemeToggle() {
  const { resolvedTheme, toggleTheme } = useTheme();
  const isDark = resolvedTheme === "dark";
  const label = isDark ? "Activar tema claro" : "Activar tema oscuro";

  return (
    <Tooltip.Root>
      <Tooltip.Trigger asChild>
        <Button variant="icon" type="button" onClick={toggleTheme} aria-label={label}>
          {isDark ? <Sun aria-hidden="true" /> : <Moon aria-hidden="true" />}
        </Button>
      </Tooltip.Trigger>
      <Tooltip.Portal>
        <Tooltip.Content className="tooltip" sideOffset={8}>
          {label}
          <Tooltip.Arrow className="tooltip__arrow" />
        </Tooltip.Content>
      </Tooltip.Portal>
    </Tooltip.Root>
  );
}
