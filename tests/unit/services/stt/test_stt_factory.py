import pytest

from app.services.stt.stt_factory import STTFactory


@pytest.fixture(autouse=True)
def clear_stt_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(STTFactory, "_stts", {})


def test_get_stt_reuses_the_same_whisper_instance(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    created_instances: list[object] = []

    class FakeWhisperSTT:
        def __init__(self) -> None:
            created_instances.append(self)

    monkeypatch.setattr("app.services.stt.stt_factory.WhisperSTT", FakeWhisperSTT)

    first = STTFactory.get_stt("whisper")
    second = STTFactory.get_stt("whisper")

    assert first is second
    assert len(created_instances) == 1
    assert isinstance(first, FakeWhisperSTT)


def test_get_stt_raises_for_invalid_provider() -> None:
    with pytest.raises(ValueError, match="Invalid STT provider: invalid"):
        STTFactory.get_stt("invalid")
