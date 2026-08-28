from pathlib import Path
from typing import Protocol

import numpy as np


class BaseTTS(Protocol):
    def load(self, voice_name: str, *, device: str | None = None) -> None:
        pass

    def generate(
        self, text: str, *, voice: str | None = None, speed: float = 1.0
    ) -> np.ndarray:
        pass

    def generate_wav(
        self, text: str, *, voice: str | None = None, speed: float = 1.0
    ) -> bytes:
        pass

    def save(self, audio: np.ndarray, filename: str | Path) -> None:
        pass
