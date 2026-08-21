# Repository Guidelines

## Project Structure & Module Organization

Application code lives in `app/`. The FastAPI entry point is `app/app.py`, while
`main.py` exposes the application for local execution. API endpoints are grouped
under `app/api/v1/routes/`. LangGraph construction, state, persistence, and nodes
belong in `app/graph/`; keep feature-specific nodes in their own subdirectories.
Speech clients live in `app/services/stt/` and `app/services/tts/`, with shared
interfaces in each service's `common/` directory. Configuration and logging are
under `app/core/`. Tests mirror this layout in `tests/unit/`.

## Build, Test, and Development Commands

Use UV for all Python environment and dependency operations:

- `uv sync --dev`: install locked runtime and development dependencies.
- `uv run fastapi dev app/app.py`: start the API with automatic reload.
- `uv run pytest`: run the complete test suite.
- `uv run ruff format .`: format Python files.
- `uv run ruff check .`: run lint and import-order checks.
- `uv run pyrefly check`: run static type checking.
- `uv run pre-commit install`: install repository quality hooks locally.
- `uv run pre-commit run --all-files`: execute every configured hook.

Redis must be available locally for LangGraph checkpoint persistence.

## Coding Style & Naming Conventions

Target Python 3.13 and use four-space indentation. Ruff enforces an 88-character
line length and the `E`, `F`, `I`, and `UP` rule sets. Use `snake_case` for
functions, modules, and variables; `PascalCase` for classes and Pydantic models;
and descriptive node names such as `offer_scraper_node`. Add type annotations to
public functions and return partial state dictionaries from LangGraph nodes.

## Testing Guidelines

Use pytest. Name files `test_<module>.py` and tests `test_<behavior>()`. Place
focused tests beside the corresponding layer under `tests/unit/`. Mock external
services such as Langfuse, Hugging Face, Redis, STT, and TTS; do not require model
downloads or network access in unit tests. Add regression tests for graph routing,
thread IDs, checkpoints, and HITL resume behavior.

## Commit & Pull Request Guidelines

The history currently contains only short setup commits, so no strict convention
is established. Use concise, imperative subjects, optionally with a scope, for
example `graph: resume pending HITL interaction`. Pull requests should explain the
behavioral change, list verification commands, link relevant issues, and document
API or configuration changes. Include screenshots only for visible UI changes.

## Security & Configuration

Keep Langfuse, Hugging Face, and other credentials in environment variables or a
local `.env`; never commit secrets. Avoid committing generated audio, model files,
Redis data, or local virtual environments.
