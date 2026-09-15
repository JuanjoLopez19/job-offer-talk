# Repository Guidelines

## Product Context

JobTalk turns a job-offer URL into a guided interview practice session. The
product extracts the vacancy, summarizes the role, generates targeted questions,
evaluates each answer, and continues the interview with actionable feedback.
Candidates can answer with text or voice, and assistant speech is optional.

The expected user flow is: start a fresh session, submit one HTTP(S) vacancy URL,
inspect the extracted offer context, answer one question at a time, receive
feedback, and reset or leave the session. Do not add claims, analytics, persistent
browser history, or data retention beyond behavior implemented in the code.

## Architecture and Project Structure

- `app/app.py` creates the FastAPI application and lazy STT/TTS runtimes.
- `app/api/v1/` owns HTTP and WebSocket routes, connection management, and voice
  protocol validation.
- `app/graph/` owns LangGraph state, graph construction, Redis checkpoints,
  session serialization, HITL nodes, and the welcome, offer-scraper, and interview
  subgraphs.
- `app/services/` contains the LLM factory plus STT and TTS interfaces and
  implementations. Keep provider-specific code behind these factories.
- `app/core/` contains settings and logging; `app/shared/` contains models and
  utilities shared across layers.
- `frontend/src/` is the React/TypeScript client. Reusable UI belongs in
  `components/`, domain behavior in `features/`, routes in `pages/`, and global
  visual tokens in `styles/index.css`.
- `tests/unit/` mirrors the backend structure. Frontend tests stay beside the
  component or hook they cover.
- `designs/` contains editable Pen designs and presentation renders. Runtime web
  assets belong in `frontend/public/`.

FastAPI and the frontend are independently deployable. FastAPI must not serve or
write frontend files. Vite proxies `/v1` during development; production hosting
must provide an equivalent HTTP and WebSocket proxy.

## Graph and Session Invariants

- Preserve the flow `welcome -> offer scraper -> question generator -> interview
  loop` and its human-in-the-loop interruptions unless a feature explicitly
  changes the conversation model.
- A resume must use the same session/thread identifier. `X-Thread-ID` and
  `GraphInput.session_id` accept 1–128 characters.
- `GraphManager` serializes invocations per thread. Do not bypass that boundary or
  introduce concurrent graph mutations for the same session.
- Redis checkpoints expire after 3,600 seconds by default. Treat them as temporary
  session state, not durable user history.
- Graph nodes return partial state dictionaries, set their node and conditional
  edge fields, and leave routing decisions to the subgraph builders.
- Keep graph rendering explicit through `GraphManager.export_graph()`. Request
  handling must not write `graph.png` or depend on a remote renderer.
- Scraping, LLM, Redis, Langfuse, STT, and TTS failures must return controlled
  product messages or protocol errors without leaking secrets or internal traces.

## API and Voice Contracts

- `POST /v1/graph/` starts or resumes text turns. Preserve the response model and
  return the resolved `X-Thread-ID` header.
- `WS /v1/conversation/{session_id}` receives one JSON metadata frame followed by
  one binary audio frame per turn.
- Voice metadata uses event `user_message`, a supported MIME type, a 1–64
  character `turn_id`, and the `is_tts_active` flag.
- Supported audio types are MP4, OGG, WAV, WebM, and x-wav; the maximum payload is
  10 MiB. Invalid metadata closes the socket with policy code 1008, while invalid
  audio size reports a turn-scoped error and keeps the connection available.
- Keep STT and TTS lazy so model downloads and initialization do not block
  application startup or unit tests.

## Frontend Conventions

Use TypeScript for all frontend source. Keep API payload types in the interview
feature, network behavior in its API/hooks, and presentation in components. Use
composition over page-sized components with mixed transport and UI logic.

Preserve these product behaviors:

- Each visit creates an independent in-memory browser session; do not add local or
  session storage for conversation history without an explicit requirement.
- The initial turn accepts a valid HTTP(S) offer URL and hides voice input. Later
  turns accept text or microphone input.
- Assistant HTML is sanitized before rendering. Never use unsanitized
  `dangerouslySetInnerHTML`.
- Every control needs an accessible name, keyboard focus, disabled/loading state,
  and useful error feedback. Decorative brand images use empty alt text.
- Reuse CSS custom properties for light/dark themes and keep layouts usable from
  320 px upward. Respect the current IBM Plex Mono and restrained terminal visual
  language.
- Resolve public assets with `import.meta.env.BASE_URL` in application code and
  `%BASE_URL%` in `index.html` so static deployments keep working under a base
  path.

## Tooling and Commands

Python targets 3.13. Use UV for environments and dependency changes, Ruff for
formatting/linting, Pyrefly for type checking, and pytest for tests:

- `uv sync --dev --extra google`: install the default development environment.
- `uv run fastapi dev app/app.py`: start the API with reload.
- `uv run ruff format .`: format Python files.
- `uv run ruff check .`: lint and check import order.
- `uv run pyrefly check`: type-check application code.
- `uv run pytest`: run backend tests.
- `uv run pre-commit install`: install Python quality hooks.
- `uv run pre-commit run --all-files`: execute all pre-commit checks.

Use pnpm for every Node.js operation and Biome for formatting/linting:

- `pnpm install`: install workspace dependencies and configure Husky.
- `pnpm dev:frontend`: start Vite on port 5173.
- `pnpm check`: run Biome without rewriting files.
- `pnpm --dir frontend format`: apply Biome formatting.
- `pnpm test:frontend`: run Vitest.
- `pnpm build`: run TypeScript compilation and create the Vite build.

Do not use pip, npm, yarn, Prettier, ESLint, Black, isort, mypy, or ad-hoc package
installation in this repository. Update `uv.lock` or `pnpm-lock.yaml` whenever the
corresponding manifest changes.

Husky's pre-commit hook must continue to run the Python pre-commit suite, Biome,
and frontend tests. When adding a new quality tool, integrate it into the relevant
hook at project setup time.

## Coding Style

Python uses four spaces, an 88-character line length, public type annotations,
`snake_case` functions/modules/variables, and `PascalCase` classes and Pydantic
models. Ruff enforces `E`, `F`, `I`, and `UP`. Prefer focused nodes and services
over multi-purpose classes.

TypeScript must remain strict. Use function components, explicit props and domain
types, semantic HTML, and existing primitives before adding dependencies. Avoid
`any`, unchecked casts, transport logic in JSX, and duplicated server state.

## Testing and Acceptance

Name backend files `test_<module>.py` and tests `test_<behavior>()`. Mock all
external systems: LLM providers, Langfuse, Redis, scrapers, model downloads, STT,
and TTS. Unit tests must not require network access, credentials, CUDA, or a live
Redis instance.

Add regression tests when changing graph routing, state updates, thread IDs,
checkpoint behavior, HITL resume logic, session locking, protocol errors, voice
turn correlation, sanitized content, URL validation, reset behavior, theme, or
responsive navigation. Use Testing Library queries that reflect user-visible
roles and labels.

Before handoff, run Ruff formatting/checks, Pyrefly, pytest, Biome, Vitest, and the
frontend build. Run the full pre-commit suite when changes span both stacks.

## Security, Configuration, and Assets

Settings come from `.env` and `.env.local` using nested `__` delimiters. Never
commit provider keys, Langfuse credentials, generated audio, model weights,
Redis files, local environments, caches, or build output. Logs and user-facing
errors must not expose offer contents beyond the current response, credentials,
stack traces, or raw model configuration.

Generated visual assets must be original, have no third-party marks or watermarks,
and be stored under the consuming package. Keep high-resolution source assets when
useful, verify transparency and small-size legibility for icons, and reference
Vite public assets through the configured base path.

## Commits and Pull Requests

Use concise imperative subjects, optionally scoped, such as `graph: resume pending
HITL interaction`. Pull requests must describe the behavior change, list
verification commands, link relevant issues, and call out API, environment, data,
or deployment changes. Include screenshots for visible interface changes.
