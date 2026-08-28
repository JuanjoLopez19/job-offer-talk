# job-offer-talk

Job Offer Talk.

## Configurar Gemini

1. Copia `.env.example` a `.env` y completa las variables necesarias.
2. Crea una clave de API en el proyecto de Google Cloud y restríngela a
   **Gemini API** (`generativelanguage.googleapis.com`).
3. Guarda la clave solamente en `GOOGLE_API_KEY` dentro de `.env.local`. Este
   archivo tiene prioridad sobre `.env` y está excluido de Git.
4. Opcionalmente, cambia `GOOGLE_MODEL`; por defecto se usa
   `gemini-3.7-flash`.

Instala el entorno y ejecuta los controles de calidad con:

```powershell
uv sync --dev
uv run pre-commit install
uv run pre-commit run --all-files
```
