import pytest

from app.core.config import TtsProvider
from app.services.tts.tts_factory import TTSFactory


@pytest.fixture(autouse=True)
def clear_tts_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(TTSFactory, "_ttss", {})


def test_get_tts_reuses_the_same_kokoro_instance(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    created_instances: list[object] = []

    class FakeKokoroTTS:
        def __init__(self) -> None:
            created_instances.append(self)

    monkeypatch.setattr("app.services.tts.tts_factory.KokoroTTS", FakeKokoroTTS)

    first = TTSFactory.get_tts(TtsProvider.KOKORO)
    second = TTSFactory.get_tts(TtsProvider.KOKORO)

    assert first is second
    assert len(created_instances) == 1
    assert isinstance(first, FakeKokoroTTS)


def test_get_tts_raises_for_invalid_provider() -> None:
    with pytest.raises(ValueError, match="Invalid TTS provider: invalid"):
        TTSFactory.get_tts("invalid")  # type: ignore[arg-type]
