import * as AlertDialog from "@radix-ui/react-alert-dialog";
import { Plus } from "lucide-react";
import { Button } from "../../components/ui/Button";

export function ResetSessionDialog({ onReset }: { onReset: () => void }) {
  return (
    <AlertDialog.Root>
      <AlertDialog.Trigger asChild>
        <Button className="session-reset">
          <Plus aria-hidden="true" /> Nueva sesión
        </Button>
      </AlertDialog.Trigger>
      <AlertDialog.Portal>
        <AlertDialog.Overlay className="dialog-overlay" />
        <AlertDialog.Content className="dialog-content">
          <AlertDialog.Title>¿Empezar de nuevo?</AlertDialog.Title>
          <AlertDialog.Description>
            Se borrarán los mensajes de esta visita y JobTalk te pedirá otra oferta.
          </AlertDialog.Description>
          <div className="dialog-actions">
            <AlertDialog.Cancel asChild>
              <Button variant="secondary">Cancelar</Button>
            </AlertDialog.Cancel>
            <AlertDialog.Action asChild>
              <Button onClick={onReset}>Nueva sesión</Button>
            </AlertDialog.Action>
          </div>
        </AlertDialog.Content>
      </AlertDialog.Portal>
    </AlertDialog.Root>
  );
}
