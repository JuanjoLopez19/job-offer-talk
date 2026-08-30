from io import BytesIO
from pathlib import Path

import numpy as np
import pytest

from app.services.stt.implementations.whisper_stt import WHISPER_SAMPLE_RATE, WhisperSTT


class FakeSegment:
    def __init__(self, text: str) -> None:
        self.text = text


class FakeWhisperClient:
    def __init__(self) -> None:
        self.audio: np.ndarray | None = None

    def transcribe(self, audio: np.ndarray, *, language: str):
        self.audio = audio
        return iter([FakeSegment(" Hola"), FakeSegment("mundo ")]), None


def test_transcribe_bytes_decodes_audio_at_whisper_sample_rate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = FakeWhisperClient()
    decoded_audio = np.array([0.1, 0.2], dtype=np.float64)

    def fake_decode_audio(audio: BytesIO, sampling_rate: int) -> np.ndarray:
        assert audio.read() == b"encoded-audio"
        assert sampling_rate == WHISPER_SAMPLE_RATE
        return decoded_audio

    monkeypatch.setattr(
        "app.services.stt.implementations.whisper_stt.decode_audio", fake_decode_audio
    )
    service = WhisperSTT(client=client)  # type: ignore[arg-type]

    assert service.transcribe_bytes(b"encoded-audio") == "Hola\nmundo"
    assert client.audio is not None
    assert client.audio.dtype == np.float32
    assert client.audio.flags.c_contiguous


def test_transcribe_file_decodes_mono_audio_at_whisper_sample_rate(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    audio_path = tmp_path / "recording.mp3"
    audio_path.touch()
    client = FakeWhisperClient()
    decoded_audio = np.array([0.1, 0.2], dtype=np.float64)

    def fake_decode_audio(path: str, sampling_rate: int) -> np.ndarray:
        assert path == str(audio_path)
        assert sampling_rate == WHISPER_SAMPLE_RATE
        return decoded_audio

    monkeypatch.setattr(
        "app.services.stt.implementations.whisper_stt.decode_audio", fake_decode_audio
    )

    service = WhisperSTT(client=client)  # type: ignore[arg-type]

    assert service.transcribe_file(audio_path) == "Hola\nmundo"
    assert client.audio is not None
    assert client.audio.dtype == np.float32
    assert client.audio.flags.c_contiguous


def test_transcribe_file_raises_for_a_missing_file(tmp_path: Path) -> None:
    service = WhisperSTT()

    with pytest.raises(FileNotFoundError, match="Audio file not found"):
        service.transcribe_file(tmp_path / "missing.mp3")
