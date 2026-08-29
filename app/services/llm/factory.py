from dataclasses import dataclass
from threading import Lock
from typing import ClassVar

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama.chat_models import ChatOllama

from app.core.config import Config


@dataclass(frozen=True, slots=True)
class _LLMCacheKey:
    provider: str
    model: str
    timeout: float | None
    temperature: float
    max_tokens: int | None
    max_retries: int
    thinking_level: str


class LLMFactory:
    config: ClassVar[Config] = Config()
    allowed_providers: ClassVar[list[str]] = ["google", "ollama"]
    _llms: ClassVar[dict[_LLMCacheKey, ChatGoogleGenerativeAI | ChatOllama]] = {}
    _lock: ClassVar[Lock] = Lock()

    @classmethod
    def get_llm(
        cls,
        *,
        timeout: float | None = None,
        temperature: float = 1.0,
        max_tokens: int | None = None,
        max_retries: int = 2,
        thinking_level: str = "minimal",
    ) -> ChatGoogleGenerativeAI | ChatOllama:
        key = cls._build_cache_key(
            timeout=timeout,
            temperature=temperature,
            max_tokens=max_tokens,
            max_retries=max_retries,
            thinking_level=thinking_level,
        )
        cached_llm = cls._llms.get(key)
        if cached_llm is not None:
            return cached_llm

        with cls._lock:
            cached_llm = cls._llms.get(key)
            if cached_llm is None:
                cached_llm = cls._create_llm(key)
                cls._llms[key] = cached_llm

        return cached_llm

    @classmethod
    def _build_cache_key(
        cls,
        *,
        timeout: float | None,
        temperature: float,
        max_tokens: int | None,
        max_retries: int,
        thinking_level: str,
    ) -> _LLMCacheKey:
        if cls.config.llm_provider not in cls.allowed_providers:
            raise ValueError(f"Invalid LLM provider: {cls.config.llm_provider}")

        model = (
            cls.config.google_model
            if cls.config.llm_provider == "google"
            else cls.config.ollama_model
        )
        return _LLMCacheKey(
            provider=cls.config.llm_provider,
            model=model,
            timeout=timeout,
            temperature=temperature,
            max_tokens=max_tokens,
            max_retries=max_retries,
            thinking_level=thinking_level,
        )

    @classmethod
    def _create_llm(cls, key: _LLMCacheKey) -> ChatGoogleGenerativeAI | ChatOllama:
        if key.provider == "google":
            return ChatGoogleGenerativeAI(
                model=key.model,
                api_key=cls.config.google_api_key,
                temperature=key.temperature,
                max_tokens=key.max_tokens,
                timeout=key.timeout,
                max_retries=key.max_retries,
                thinking_level=key.thinking_level,
            )

        return ChatOllama(
            model=key.model,
            temperature=key.temperature,
            num_predict=key.max_tokens,
        )
