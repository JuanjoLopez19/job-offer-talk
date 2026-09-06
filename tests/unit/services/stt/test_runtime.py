from app.core.config import SttProvider
from app.services.stt.runtime import LazySTT


def test_lazy_stt_loads_the_model_only_on_first_transcription(monkeypatch) -> None:
    class FakeSTT:
        load_calls = 0

        def load(self, model_name: str, *, device: str | None = None) -> None:
            assert model_name == "small"
            assert device == "cpu"
            self.load_calls += 1

        def transcribe_bytes(self, audio: bytes) -> str:
            return audio.decode()

    fake_stt = FakeSTT()
    monkeypatch.setattr(
        "app.services.stt.runtime.STTFactory.get_stt",
        lambda **_: fake_stt,
    )
    runtime = LazySTT(provider=SttProvider.WHISPER, model_name="small", device="cpu")

    assert runtime.transcribe_bytes(b"hola") == "hola"
    assert runtime.transcribe_bytes(b"mundo") == "mundo"
    assert fake_stt.load_calls == 1
