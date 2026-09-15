from typing import Literal

from pydantic import BaseModel, Field, field_validator

MAX_AUDIO_BYTES = 10 * 1024 * 1024
SUPPORTED_AUDIO_TYPES = frozenset(
    {
        "audio/mp4",
        "audio/ogg",
        "audio/wav",
        "audio/webm",
        "audio/x-wav",
    }
)


class VoiceMessageMetadata(BaseModel):
    event: Literal["user_message"]
    content_type: str
    is_tts_active: bool = False
    turn_id: str = Field(min_length=1, max_length=64)

    @field_validator("content_type")
    @classmethod
    def validate_content_type(cls, value: str) -> str:
        normalized = value.split(";", maxsplit=1)[0].strip().lower()
        if normalized not in SUPPORTED_AUDIO_TYPES:
            raise ValueError("unsupported audio type")
        return value


def validate_audio_size(audio: bytes) -> None:
    if not audio:
        raise ValueError("El audio está vacío")
    if len(audio) > MAX_AUDIO_BYTES:
        raise ValueError("El audio supera el límite de 10 MB")
