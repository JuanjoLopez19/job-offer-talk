from threading import Lock
from typing import ClassVar

from app.core.config import TtsProvider
from app.services.tts.common.base import BaseTTS
from app.services.tts.implementations.kokoro_tts import KokoroTTS


class TTSFactory:
    allowed_providers: ClassVar[list[TtsProvider]] = list(TtsProvider)
    _ttss: ClassVar[dict[TtsProvider, BaseTTS]] = {}
    _lock: ClassVar[Lock] = Lock()

    @classmethod
    def get_tts(cls, tts_provider: TtsProvider) -> BaseTTS:
        cached_tts = cls._ttss.get(tts_provider)
        if cached_tts is not None:
            return cached_tts

        with cls._lock:
            cached_tts = cls._ttss.get(tts_provider)
            if cached_tts is None:
                cached_tts = cls._create_tts(tts_provider)
                cls._ttss[tts_provider] = cached_tts

        return cached_tts

    @classmethod
    def _create_tts(cls, tts_provider: TtsProvider) -> BaseTTS:
        if tts_provider == TtsProvider.KOKORO:
            return KokoroTTS()
        else:
            raise ValueError(f"Invalid TTS provider: {tts_provider}")
