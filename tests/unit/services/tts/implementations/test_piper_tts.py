import wave

import numpy as np
from piper.config import SynthesisConfig
import pytest

from app.services.tts.implementations import piper_tts as module
from app.services.tts.implementations.piper_tts import PiperTTS


class FakePiperVoice:
    class config:
        sample_rate = 16000

    def __init__(self) -> None:
        self.calls: list[tuple[str, float]] = []

    def synthesize_wav(
        self, text: str, output: wave.Wave_write, *, syn_config: SynthesisConfig
    ) -> None:
        self.calls.append((text, syn_config.length_scale))
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(16000)
        output.writeframes(np.array([0, 16384], dtype=np.int16).tobytes())


def test_load_uses_model_path_and_cuda_setting(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: dict[str, object] = {}
    client = FakePiperVoice()

    def fake_load(model_path: str, *, use_cuda: bool) -> FakePiperVoice:
        calls.update(model_path=model_path, use_cuda=use_cuda)
        return client

    monkeypatch.setattr(module.PiperVoice, "load", fake_load)
    service = PiperTTS()

    service.load("/models/es_voice.onnx", device="cuda")

    assert calls == {"model_path": "/models/es_voice.onnx", "use_cuda": True}
    assert service.sample_rate == 16000


def test_generate_returns_normalized_float_audio() -> None:
    client = FakePiperVoice()
    service = PiperTTS(client=client)

    audio = service.generate("<b>Hola</b>", speed=2.0)

    assert audio.dtype == np.float32
    assert np.allclose(audio, [0.0, 0.5], atol=1e-4)
    assert client.calls == [("Hola", 0.5)]


def test_generate_rejects_invalid_speed() -> None:
    service = PiperTTS(client=FakePiperVoice())

    with pytest.raises(ValueError, match="greater than zero"):
        service.generate("Hola", speed=0)


def test_generate_requires_a_loaded_client() -> None:
    with pytest.raises(RuntimeError, match="not loaded"):
        PiperTTS().generate("Hola")
