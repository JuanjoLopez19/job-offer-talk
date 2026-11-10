from pathlib import Path

from app.services.tts import piper_voice


class FakeResponse:
    def __init__(self, content: bytes) -> None:
        self.content = content

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *_: object) -> None:
        pass

    def read(self, _: int) -> bytes:
        content, self.content = self.content, b""
        return content


def test_ensure_piper_voice_downloads_model_and_config(
    monkeypatch, tmp_path: Path
) -> None:
    urls: list[str] = []

    def fake_urlopen(url: str, *, timeout: int) -> FakeResponse:
        urls.append(url)
        return FakeResponse(b"voice")

    monkeypatch.setattr(piper_voice, "urlopen", fake_urlopen)

    model_path = piper_voice.ensure_piper_voice(
        "es_ES-davefx-medium",
        tmp_path,
    )

    assert model_path == tmp_path / "es_ES-davefx-medium.onnx"
    assert model_path.read_bytes() == b"voice"
    assert model_path.with_suffix(".onnx.json").read_bytes() == b"voice"
    assert urls == [
        f"{piper_voice.PIPER_VOICE_BASE_URL}/es_ES-davefx-medium.onnx",
        f"{piper_voice.PIPER_VOICE_BASE_URL}/es_ES-davefx-medium.onnx.json",
    ]


def test_ensure_piper_voice_reuses_complete_cached_model(
    monkeypatch, tmp_path: Path
) -> None:
    model_path = tmp_path / "es_ES-davefx-medium.onnx"
    config_path = model_path.with_suffix(".onnx.json")
    model_path.write_bytes(b"voice")
    config_path.write_bytes(b"config")
    monkeypatch.setattr(
        piper_voice,
        "urlopen",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("cached voice should not be downloaded")
        ),
    )

    assert piper_voice.ensure_piper_voice("es_ES-davefx-medium", tmp_path) == model_path
