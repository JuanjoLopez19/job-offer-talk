from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.__init_ import main_router
from app.core.logger import suppress_model_loading_noise
from app.frontend import mount_frontend
from app.services.stt.runtime import LazySTT


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.core.config import Config

    suppress_model_loading_noise()
    config = Config()

    app.state.config = config
    app.state.stt = LazySTT(
        provider=config.stt.provider,
        model_name=config.stt.model_name,
        device=config.stt.device,
    )

    yield


app = FastAPI(
    title="JobTalk API",
    description="Entrevistas guiadas a partir de una oferta de empleo.",
    lifespan=lifespan,
)
app.include_router(main_router)
mount_frontend(app)
