from dataclasses import dataclass, field
from threading import Lock

from app.core.config import SttProvider
from app.services.stt.common.base import BaseSTT
from app.services.stt.stt_factory import STTFactory


@dataclass(slots=True)
class LazySTT:
    """Load the speech model on first use so API startup stays lightweight."""

    provider: SttProvider
    model_name: str
    device: str
    _client: BaseSTT | None = field(default=None, init=False)
    _lock: Lock = field(default_factory=Lock, init=False)

    def transcribe_bytes(self, audio: bytes) -> str:
        return self._get_client().transcribe_bytes(audio)

    def _get_client(self) -> BaseSTT:
        if self._client is not None:
            return self._client

        with self._lock:
            if self._client is None:
                client = STTFactory.get_stt(stt_provider=self.provider)
                client.load(self.model_name, device=self.device)
                self._client = client
        return self._client
