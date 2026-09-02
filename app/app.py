from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.__init_ import main_router
from app.core.logger import suppress_model_loading_noise

# from app.services.stt.stt_factory import STTFactory
# from app.services.tts.tts_factory import TTSFactory


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.core.config import Config

    suppress_model_loading_noise()
    config = Config()

    # stt = STTFactory.get_stt(stt_provider=config.stt.provider)
    # tts = TTSFactory.get_tts(tts_provider=config.tts.provider)
    # app.state.stt = stt
    # app.state.tts = tts
    app.state.config = config

    yield


app = FastAPI(lifespan=lifespan)
app.include_router(main_router)
