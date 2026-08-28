import json
import logging
import warnings
from collections.abc import Iterator
from typing import Any, cast

import pytest
import structlog

from app.core import logger as logger_module
from app.core.logger import get_logger, setup_logging, suppress_model_loading_noise


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


def test_suppress_model_loading_noise_filters_only_known_warnings() -> None:
    with warnings.catch_warnings(record=True) as caught_warnings:
        warnings.simplefilter("always")
        suppress_model_loading_noise()

        warnings.warn_explicit(
            "dropout option adds dropout after all but last recurrent layer",
            UserWarning,
            filename="rnn.py",
            lineno=1,
            module="torch.nn.modules.rnn",
        )
        warnings.warn_explicit(
            "`torch.nn.utils.weight_norm` is deprecated in favor of "
            "`torch.nn.utils.parametrizations.weight_norm`.",
            FutureWarning,
            filename="weight_norm.py",
            lineno=1,
            module="torch.nn.utils.weight_norm",
        )
        warnings.warn("application warning", UserWarning, stacklevel=1)

    assert [str(warning.message) for warning in caught_warnings] == [
        "application warning"
    ]


def test_suppress_model_loading_noise_filters_hugging_face_auth_message() -> None:
    suppress_model_loading_noise()
    logger = logging.getLogger("huggingface_hub.utils._http")
    record = logger.makeRecord(
        logger.name,
        logging.WARNING,
        __file__,
        0,
        "You are sending unauthenticated requests to the HF Hub.",
        (),
        None,
    )

    assert any(
        not cast(Any, warning_filter).filter(record)
        for warning_filter in logger.filters
    )


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
