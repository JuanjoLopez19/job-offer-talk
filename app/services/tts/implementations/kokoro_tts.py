import os
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

import numpy as np
import soundfile as sf
from kokoro import KPipeline

from app.services.tts.common.base import BaseTTS

SAMPLE_RATE = 24000


@dataclass(slots=True)
class KokoroTTS(BaseTTS):
    client: KPipeline | None = None
    voice_name: str = "em_alex"

    def load(self, voice_name: str, *, device: str | None = None) -> None:
        self.voice_name = voice_name
        selected_device = device or os.getenv("KOKORO_DEVICE") or None
        self.client = KPipeline(
            lang_code="e", repo_id="hexgrad/Kokoro-82M", device=selected_device
        )

    def generate(
        self, text: str, *, voice: str | None = None, speed: float = 1.0
    ) -> np.ndarray:
        if self.client is None:
            raise RuntimeError("KokoroTTS is not loaded")
        if not text.strip():
            raise ValueError("Text to synthesize cannot be empty")

        selected_voice = voice or self.voice_name
        chunks: list[np.ndarray] = []
        for _, _, audio in self.client(text, voice=selected_voice, speed=speed):
            if audio is None:
                continue
            if hasattr(audio, "cpu"):
                audio = audio.cpu().numpy()
            chunks.append(np.asarray(audio, dtype=np.float32))

        if not chunks:
            raise RuntimeError("No audio generated")

        return np.concatenate(chunks)

    def generate_bytes(
        self, text: str, *, voice: str | None = None, speed: float = 1.0
    ) -> bytes:
        audio = self.generate(text, voice=voice, speed=speed)
        buffer = BytesIO()
        sf.write(buffer, audio, SAMPLE_RATE, format="WAV", subtype="PCM_16")
        return buffer.getvalue()

    def save(self, audio: np.ndarray, filename: str | Path) -> None:
        output_path = Path(filename)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        sf.write(output_path, audio, SAMPLE_RATE, subtype="PCM_16")
