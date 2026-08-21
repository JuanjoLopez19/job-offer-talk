import json
import logging
from collections.abc import Iterator

import pytest
import structlog

from app.core import logger as logger_module
from app.core.logger import get_logger, setup_logging


@pytest.fixture(autouse=True)
def reset_logging() -> Iterator[None]:
    yield
    logger_module._configured = False
    structlog.reset_defaults()
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(logging.WARNING)


def test_json_format_emits_a_structured_event(
    capsys: pytest.CaptureFixture[str],
) -> None:
    setup_logging(log_format="json", log_level="INFO")

    get_logger("stt").info("transcription complete", duration_s=1.2)

    payload = json.loads(capsys.readouterr().out.strip())
    assert payload["event"] == "transcription complete"
    assert payload["level"] == "info"
    assert payload["logger"] == "app.stt"
    assert payload["duration_s"] == 1.2
    assert "timestamp" in payload


def test_console_format_emits_human_readable_text(
    capsys: pytest.CaptureFixture[str],
) -> None:
    setup_logging(log_format="console", log_level="INFO")

    get_logger("tts").info("speech saved")

    output = capsys.readouterr().out
    assert "speech saved" in output
    with pytest.raises(json.JSONDecodeError):
        json.loads(output)


def test_info_level_drops_debug_events(capsys: pytest.CaptureFixture[str]) -> None:
    setup_logging(log_format="json", log_level="INFO")
    logger = get_logger("app")

    logger.debug("skip me")
    logger.info("keep me")

    payload = json.loads(capsys.readouterr().out.strip())
    assert payload["event"] == "keep me"


def test_stdlib_module_loggers_are_silenced(
    capsys: pytest.CaptureFixture[str],
) -> None:
    setup_logging(log_format="json", log_level="INFO")

    logging.getLogger("uvicorn").info("application startup")

    assert capsys.readouterr().out == ""


def test_setup_logging_reads_format_from_env(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("LOG_FORMAT", "json")
    monkeypatch.setenv("LOG_LEVEL", "WARNING")
    setup_logging()

    get_logger("app").info("too quiet")
    get_logger("app").warning("loud enough")

    payload = json.loads(capsys.readouterr().out.strip())
    assert payload["event"] == "loud enough"


def test_setup_logging_rejects_unknown_format() -> None:
    with pytest.raises(ValueError, match="Unknown log format"):
        setup_logging(log_format="xml")  # type: ignore[arg-type]


def test_setup_logging_rejects_unknown_level() -> None:
    with pytest.raises(ValueError, match="Unknown log level"):
        setup_logging(log_level="VERBOSE")
