from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.__init_ import main_router
from app.core.config import Provider, TtsProvider
from app.core.logger import get_logger, suppress_model_loading_noise
from app.services.stt.runtime import LazySTT
from app.services.tts.piper_voice import DEFAULT_PIPER_VOICE, ensure_piper_voice
from app.services.tts.runtime import LazyTTS


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
    voice_name = config.tts.voice
    if config.tts.provider == TtsProvider.PIPER:
        if voice_name == "em_alex":
            voice_name = DEFAULT_PIPER_VOICE
        voice_name = ensure_piper_voice(
            voice_name,
            config.tts.piper_model_dir,
        ).as_posix()

    app.state.tts = LazyTTS(
        provider=config.tts.provider,
        voice_name=voice_name,
        device=config.tts.device,
    )

    if config.llm_provider == Provider.OLLAMA:
        import ollama

        from app.shared.tools import check_ollama_model

        if not check_ollama_model(config.ollama_model):
            get_logger(__name__).warning(
                f"Model {config.ollama_model} not found in Ollama, pulling it..."
            )
            res = ollama.pull(config.ollama_model)
            get_logger(__name__).info(
                f"Model {config.ollama_model} pulled successfully: {res}"
            )

    yield


app = FastAPI(
    title="JobTalk API",
    description="Entrevistas guiadas a partir de una oferta de empleo.",
    lifespan=lifespan,
)
app.include_router(main_router)
