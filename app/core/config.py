from enum import StrEnum

import torch
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Provider(StrEnum):
    """Supported LLM providers."""

    GOOGLE = "google"
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class SttProvider(StrEnum):
    WHISPER = "whisper"


class TtsProvider(StrEnum):
    KOKORO = "kokoro"


class SttConfig(BaseModel):
    model_name: str = Field("medium")
    device: str = Field("cuda" if torch.cuda.is_available() else "cpu")
    provider: SttProvider = Field(SttProvider.WHISPER)


class TtsConfig(BaseModel):
    voice: str = Field("em_alex")
    device: str = Field("cuda" if torch.cuda.is_available() else "cpu")
    provider: TtsProvider = Field(TtsProvider.KOKORO)


class ReasoningLevel(BaseModel):
    """Provider-specific reasoning settings for a single canonical level."""

    google_level: str
    openai_effort: str | None
    claude_budget_tokens: int


class ReasoningLevels(BaseModel):
    """Canonical thinking levels mapped to provider-specific values."""

    minimal: ReasoningLevel
    low: ReasoningLevel
    medium: ReasoningLevel
    high: ReasoningLevel


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

    llm_provider: Provider = Field(Provider.GOOGLE)
    google_api_key: str | None = None
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None

    google_model: str = Field("gemini-3.5-flash-lite")
    ollama_model: str = Field("gemma4:e2b")
    openai_model: str = Field("gpt-4o-mini")
    anthropic_model: str = Field("claude-3-5-sonnet")

    reasoning_levels: ReasoningLevels = Field(
        default=ReasoningLevels(
            minimal=ReasoningLevel(
                google_level="minimal",
                openai_effort="low",
                claude_budget_tokens=1024,
            ),
            low=ReasoningLevel(
                google_level="low",
                openai_effort="low",
                claude_budget_tokens=2048,
            ),
            medium=ReasoningLevel(
                google_level="medium",
                openai_effort="medium",
                claude_budget_tokens=8192,
            ),
            high=ReasoningLevel(
                google_level="high",
                openai_effort="high",
                claude_budget_tokens=16384,
            ),
        )
    )
