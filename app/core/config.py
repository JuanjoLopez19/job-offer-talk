import torch
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class SttConfig(BaseModel):
    model_name: str = Field("medium")
    device: str = Field("cuda" if torch.cuda.is_available() else "cpu")


class TtsConfig(BaseModel):
    voice: str = Field("em_alex")
    device: str = Field("cuda" if torch.cuda.is_available() else "cpu")


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"),
        env_nested_delimiter="__",
    )

    environment: str = Field("DEV")
    version: str = Field("0.0.1")

    stt: SttConfig
    tts: TtsConfig

    langfuse_secret_key: str
    langfuse_public_key: str
    langfuse_base_url: str
    langfuse_trace_name: str = Field("job-offer-talk")

    llm_provider: str = Field("google")
    google_api_key: str
    google_model: str = Field("gemini-3.5-flash-lite")
    ollama_model: str = Field("gemma4:e2b")
