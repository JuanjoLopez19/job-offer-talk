import os
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

import numpy as np
import torch
from faster_whisper import WhisperModel
from faster_whisper.audio import decode_audio

from app.core.logger import get_logger
from app.services.stt.common.base import BaseSTT

WHISPER_SAMPLE_RATE = 16_000


@dataclass(slots=True)
class WhisperSTT(BaseSTT):
    client: WhisperModel | None = None

    def load(self, model_name: str, *, device: str | None = None) -> None:
        selected_device = device or os.getenv("WHISPER_DEVICE")
        if selected_device is None:
            selected_device = "cuda" if torch.cuda.is_available() else "cpu"

        self.client = WhisperModel(model_name, device=selected_device)
        get_logger(__name__).info(
            f"Loaded Whisper model {model_name} on device {selected_device} successfully"
        )

    def transcribe(self, audio: np.ndarray) -> str:
        if self.client is None:
            raise RuntimeError("WhisperSTT is not loaded")

        segments, _ = self.client.transcribe(audio, language="es")
        return "\n".join(segment.text.strip() for segment in segments).strip()

    def transcribe_bytes(self, audio: bytes) -> str:
        decoded_audio = decode_audio(
            BytesIO(audio),
            sampling_rate=WHISPER_SAMPLE_RATE,
        )
        return self.transcribe(np.ascontiguousarray(decoded_audio, dtype=np.float32))

    def transcribe_file(self, audio_file: str | Path) -> str:
        audio_path = Path(audio_file)
        if not audio_path.is_file():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        audio = decode_audio(str(audio_path), sampling_rate=WHISPER_SAMPLE_RATE)
        return self.transcribe(np.ascontiguousarray(audio, dtype=np.float32))
