from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.__init_ import main_router
from app.core.logger import suppress_model_loading_noise
from app.services.stt.whisper_stt import WhisperSTT
from app.services.tts.kokoro_tts import KokoroTTS


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.core.config import Config

    suppress_model_loading_noise()
    config = Config()
    stt = WhisperSTT()
    tts = KokoroTTS()

    # stt.load(model_name=config.stt.model_name, device=config.stt.device)
    # tts.load(voice_name=config.tts.voice, device=config.tts.device)

    app.state.stt = stt
    app.state.tts = tts
    app.state.config = config

    yield


app = FastAPI(lifespan=lifespan)
app.include_router(main_router)
