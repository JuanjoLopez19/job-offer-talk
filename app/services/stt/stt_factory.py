from threading import Lock
from typing import ClassVar

from app.services.stt.common.base import BaseSTT
from app.services.stt.implementations.whisper_stt import WhisperSTT


class STTFactory:
    _stts: ClassVar[dict[str, BaseSTT]] = {}
    _lock: ClassVar[Lock] = Lock()

    @classmethod
    def get_stt(cls, stt_provider: str) -> BaseSTT:
        cached_stt = cls._stts.get(stt_provider)
        if cached_stt is not None:
            return cached_stt

        with cls._lock:
            cached_stt = cls._stts.get(stt_provider)
            if cached_stt is None:
                cached_stt = cls._create_stt(stt_provider)
                cls._stts[stt_provider] = cached_stt

        return cached_stt

    @classmethod
    def _create_stt(cls, stt_provider: str) -> BaseSTT:
        if stt_provider == "whisper":
            return WhisperSTT()
        else:
            raise ValueError(f"Invalid STT provider: {stt_provider}")
