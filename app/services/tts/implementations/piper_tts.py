from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
import wave

import numpy as np
from piper import PiperVoice
from piper.config import SynthesisConfig

from app.services.tts.common.base import BaseTTS
from app.shared.tools import remove_html_tags


@dataclass(slots=True)
class PiperTTS(BaseTTS):
    client: PiperVoice | None = None
    voice_name: str | None = None
    sample_rate: int = 22050

    def load(self, voice_name: str, *, device: str | None = None) -> None:
        self.voice_name = voice_name
        self.client = PiperVoice.load(
            voice_name,
            use_cuda=device == "cuda",
        )
        self.sample_rate = self.client.config.sample_rate

    def generate(
        self, text: str, *, voice: str | None = None, speed: float = 1.0
    ) -> np.ndarray:
        if self.client is None:
            raise RuntimeError("PiperTTS is not loaded")
        if not text.strip():
            raise ValueError("Text to synthesize cannot be empty")
        if speed <= 0:
            raise ValueError("Speed must be greater than zero")

        audio = self._synthesize_wav(
            remove_html_tags(text),
            length_scale=1.0 / speed,
        )
        with wave.open(BytesIO(audio), "rb") as wav_file:
            frames = wav_file.readframes(wav_file.getnframes())
            sample_width = wav_file.getsampwidth()
            if sample_width != 2:
                raise RuntimeError("Piper generated unsupported audio format")
            return (
                np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
            )

    def generate_bytes(
        self, text: str, *, voice: str | None = None, speed: float = 1.0
    ) -> bytes:
        if self.client is None:
            raise RuntimeError("PiperTTS is not loaded")
        if not text.strip():
            raise ValueError("Text to synthesize cannot be empty")
        if speed <= 0:
            raise ValueError("Speed must be greater than zero")

        return self._synthesize_wav(
            remove_html_tags(text),
            length_scale=1.0 / speed,
        )

    def save(self, audio: np.ndarray, filename: str | Path) -> None:
        output_path = Path(filename)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        pcm_audio = np.clip(audio, -1.0, 1.0)
        with wave.open(str(output_path), "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes((pcm_audio * 32767).astype(np.int16).tobytes())

    def _synthesize_wav(self, text: str, *, length_scale: float) -> bytes:
        output = BytesIO()
        synthesis_config = SynthesisConfig(length_scale=length_scale)
        with wave.open(output, "wb") as wav_file:
            self.client.synthesize_wav(  # type: ignore[union-attr]
                text, wav_file, syn_config=synthesis_config
            )
        return output.getvalue()
