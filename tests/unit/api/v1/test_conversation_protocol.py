import pytest
from pydantic import ValidationError

from app.api.v1.conversation_protocol import (
    MAX_AUDIO_BYTES,
    VoiceMessageMetadata,
    validate_audio_size,
)


def test_voice_metadata_accepts_supported_audio_with_codec() -> None:
    metadata = VoiceMessageMetadata.model_validate(
        {
            "event": "user_message",
            "content_type": "audio/webm;codecs=opus",
            "turn_id": "turn-1",
        }
    )

    assert metadata.content_type == "audio/webm;codecs=opus"


def test_voice_metadata_rejects_unsupported_content_type() -> None:
    with pytest.raises(ValidationError):
        VoiceMessageMetadata.model_validate(
            {
                "event": "user_message",
                "content_type": "application/octet-stream",
                "turn_id": "turn-1",
            }
        )


@pytest.mark.parametrize(
    "audio,message",
    [
        (b"", "El audio está vacío"),
        (b"a" * (MAX_AUDIO_BYTES + 1), "El audio supera el límite de 10 MB"),
    ],
    ids=["empty", "too-large"],
)
def test_validate_audio_size_rejects_invalid_payloads(
    audio: bytes, message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        validate_audio_size(audio)
