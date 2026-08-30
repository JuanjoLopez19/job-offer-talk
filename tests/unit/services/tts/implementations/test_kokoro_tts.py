from pathlib import Path

import numpy as np
import pytest

from app.services.tts.implementations import kokoro_tts as module
from app.services.tts.implementations.kokoro_tts import KokoroTTS


class FakeKokoroClient:
    def __call__(self, *_: object, **__: object):
        yield None, None, np.array([0.1, 0.2], dtype=np.float64)
        yield None, None, np.array([0.3], dtype=np.float64)


def test_generate_combines_audio_chunks_as_float32() -> None:
    service = KokoroTTS(client=FakeKokoroClient())  # type: ignore[arg-type]

    audio = service.generate("Hola", voice="es_voice", speed=1.2)

    assert audio.dtype == np.float32
    assert np.allclose(audio, [0.1, 0.2, 0.3])


def test_generate_rejects_empty_text() -> None:
    service = KokoroTTS(client=FakeKokoroClient())  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="cannot be empty"):
        service.generate("   ")


def test_generate_requires_a_loaded_client() -> None:
    with pytest.raises(RuntimeError, match="not loaded"):
        KokoroTTS().generate("Hola")


def test_save_writes_audio_at_the_kokoro_sample_rate(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    captured: dict[str, object] = {}

    def fake_write(
        path: Path, audio: np.ndarray, sample_rate: int, **kwargs: object
    ) -> None:
        captured.update(path=path, audio=audio, sample_rate=sample_rate, **kwargs)

    monkeypatch.setattr(module.sf, "write", fake_write)
    output_path = tmp_path / "audio" / "answer.wav"
    audio = np.array([0.1], dtype=np.float32)

    KokoroTTS().save(audio, output_path)

    assert output_path.parent.exists()
    assert captured["path"] == output_path
    assert captured["audio"] is audio
    assert captured["sample_rate"] == module.SAMPLE_RATE
    assert captured["subtype"] == "PCM_16"
