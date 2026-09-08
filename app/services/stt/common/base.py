from pathlib import Path
from typing import Protocol

import numpy as np


class BaseSTT(Protocol):
    def load(self, model_name: str, *, device: str | None = None) -> None:
        pass

    def transcribe_bytes(self, audio: bytes) -> str:
        pass

    def transcribe(self, audio: np.ndarray) -> str:
        pass

    def transcribe_file(self, audio_file: str | Path) -> str:
        pass
