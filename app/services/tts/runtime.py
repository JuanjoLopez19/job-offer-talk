from dataclasses import dataclass, field
from threading import Lock

from app.core.config import TtsProvider
from app.services.tts.common.base import BaseTTS
from app.services.tts.tts_factory import TTSFactory


@dataclass(slots=True)
class LazyTTS:
    """Load the speech model on first use so API startup stays lightweight."""

    provider: TtsProvider
    voice_name: str
    device: str
    _client: BaseTTS | None = field(default=None, init=False)
    _lock: Lock = field(default_factory=Lock, init=False)

    def generate_bytes(self, text: str) -> bytes:
        return self._get_client().generate_bytes(text, voice=self.voice_name)

    def _get_client(self) -> BaseTTS:
        if self._client is not None:
            return self._client

        with self._lock:
            if self._client is None:
                client = TTSFactory.get_tts(tts_provider=self.provider)
                client.load(self.voice_name, device=self.device)
                self._client = client
        return self._client
