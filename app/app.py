from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.__init_ import main_router
from app.core.logger import suppress_model_loading_noise


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.core.config import Config
    # from app.services.tts.kokoro_tts import KokoroTTS

    suppress_model_loading_noise()
    config = Config()

    app.state.config = config

    yield


app = FastAPI(lifespan=lifespan)
app.include_router(main_router)
