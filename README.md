# JobTalk

Asistente conversacional para preparar entrevistas a partir de una oferta de
empleo. La aplicación extrae la información de una oferta, genera preguntas
relevantes y conduce una entrevista interactiva manteniendo el estado de cada
sesión.

## Características

- Extracción de ofertas de empleo a partir de su URL.
- Generación de preguntas adaptadas al contenido de la oferta.
- Entrevista conversacional con análisis de las respuestas del usuario.
- Flujos human-in-the-loop mediante interrupciones de LangGraph.
- Persistencia temporal de sesiones y puntos de control en Redis.
- Trazabilidad de ejecuciones con Langfuse.
- Soporte para Google Gemini, OpenAI, Anthropic y modelos locales con Ollama.
- API construida con FastAPI.
- Interfaz React responsive con temas claro y oscuro.
- Un único servicio en producción: FastAPI sirve la API y el frontend compilado.

## Arquitectura del flujo

La lógica conversacional se implementa como un grafo de estados compuesto por
los subgrafos de bienvenida, extracción de la oferta y entrevista. Los nodos
`hitl` detienen la ejecución para solicitar información al usuario y la
reanundan usando el mismo identificador de sesión.

El archivo `graph.png` contiene siempre la representación actual del flujo y se
actualiza automáticamente cuando se compila e invoca el grafo.

![Grafo de estados de JobTalk](graph.png)

## Requisitos

- Python 3.13 o superior.
- [uv](https://docs.astral.sh/uv/).
- Redis disponible en `localhost:6379`.
- Credenciales de Langfuse.
- Un proveedor de LLM configurado.
- Node.js y pnpm para compilar el frontend.

El procesamiento de voz usa Faster Whisper para STT y Kokoro para TTS. Ambos
pueden utilizar CPU o CUDA según la configuración.

## Instalación

1. Clona el repositorio y entra en su directorio.
2. Instala las dependencias de desarrollo y las del proveedor que quieras usar:

   ```powershell
   # Google Gemini
   uv sync --dev --extra google

   # También están disponibles: ollama, openai, anthropic y all
   ```

3. Instala las dependencias del frontend. Este paso también configura Husky:

   ```powershell
   pnpm install
   ```

4. Copia el archivo de configuración de ejemplo:

   ```powershell
   Copy-Item .env.example .env
   ```

5. Completa en `.env` las credenciales de Langfuse y la configuración de STT y
   TTS. Guarda las claves privadas del proveedor en `.env.local`, que tiene
   prioridad sobre `.env` y está excluido de Git.

## Configuración del LLM

Google Gemini es el proveedor predeterminado. Crea una clave restringida a
**Gemini API** (`generativelanguage.googleapis.com`) y añade:

```dotenv
LLM_PROVIDER=google
GOOGLE_API_KEY=tu_clave
GOOGLE_MODEL=gemini-3.7-flash
```

Para cambiar de proveedor, instala su extra y establece `LLM_PROVIDER` como
`openai`, `anthropic` u `ollama`. Configura además la variable correspondiente:
`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `OPENAI_MODEL`, `ANTHROPIC_MODEL` u
`OLLAMA_MODEL`.

## Ejecución

Compila React, arranca Redis y después inicia FastAPI:

```powershell
pnpm build
uv run fastapi dev app/app.py
```

FastAPI sirve la landing en `http://127.0.0.1:8000/`, la entrevista en
`http://127.0.0.1:8000/entrevista` y la documentación de la API en
`http://127.0.0.1:8000/docs`. En producción solo se ejecuta FastAPI; Node se usa
exclusivamente durante la compilación.

Para trabajar en el frontend con recarga automática, ejecuta FastAPI y Vite en
terminales distintas. Vite redirige las llamadas HTTP y WebSocket a FastAPI:

```powershell
uv run fastapi dev app/app.py
pnpm dev:frontend
```

El servidor de Vite es solo para desarrollo; la entrega final continúa siendo un
único servicio FastAPI.

### Iniciar una conversación

Envía la entrada inicial a `POST /v1/graph/`:

```powershell
$body = @{
    session_id = "mi-sesion"
    user_input = $null
} | ConvertTo-Json

Invoke-RestMethod `
    -Method Post `
    -Uri "http://127.0.0.1:8000/v1/graph/" `
    -ContentType "application/json" `
    -Body $body
```

Para responder a una interrupción, realiza otra petición con el texto en
`user_input` y conserva el mismo `session_id` o la cabecera `X-Thread-ID`. El
servidor devuelve ese identificador en la misma cabecera para permitir la
continuación del flujo.

## Calidad y pruebas

```powershell
uv run ruff format .
uv run ruff check .
uv run pyrefly check
uv run pytest
pnpm check
pnpm test:frontend
pnpm build
```

`pnpm install` configura Husky. El hook ejecuta pre-commit para Python y Biome,
Vitest y TypeScript para el frontend. Para lanzar todas las comprobaciones a mano:

```powershell
uv run pre-commit run --all-files
pnpm check
pnpm test:frontend
pnpm build
```

## Estructura del proyecto

```text
app/
├── api/v1/          # Rutas HTTP, WebSocket y gestión de conexiones
├── core/            # Configuración y logging
├── graph/           # Estado, persistencia, subgrafos y nodos de LangGraph
├── services/        # Proveedores de LLM, STT y TTS
└── shared/          # Modelos compartidos
frontend/
├── src/components/  # Componentes de interfaz reutilizables
├── src/features/    # Tema, conversación, voz y cliente API
├── src/pages/       # Landing y entrevista
└── dist/            # Build generado y servido por FastAPI
tests/unit/           # Pruebas unitarias con la misma estructura que app/
graph.png             # Diagrama actualizado del grafo
```
