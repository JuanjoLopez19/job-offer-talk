from dataclasses import dataclass
from threading import Lock
from typing import ClassVar, assert_never

from langchain_core.language_models import BaseChatModel

from app.core.config import Config, Provider, ReasoningLevel, ReasoningLevels


@dataclass(frozen=True, slots=True)
class _LLMCacheKey:
    provider: Provider
    model: str
    timeout: float | None
    temperature: float
    max_tokens: int | None
    max_retries: int
    thinking_level: str


class LLMFactory:
    config: ClassVar[Config] = Config()
    allowed_providers: ClassVar[list[Provider]] = list(Provider)
    _llms: ClassVar[dict[_LLMCacheKey, BaseChatModel]] = {}
    _lock: ClassVar[Lock] = Lock()

    @classmethod
    def get_llm(
        cls,
        *,
        model_name: str | None = None,
        timeout: float | None = None,
        temperature: float = 1.0,
        max_tokens: int | None = None,
        max_retries: int = 2,
        thinking_level: str = "minimal",
    ) -> BaseChatModel:
        key = cls._build_cache_key(
            model_name=model_name,
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
        model_name: str | None,
        timeout: float | None,
        temperature: float,
        max_tokens: int | None,
        max_retries: int,
        thinking_level: str,
    ) -> _LLMCacheKey:
        # Fail-fast on invalid thinking levels instead of deferring the error
        # until the LLM client is instantiated.
        cls._resolve_reasoning(thinking_level)

        provider = cls.config.llm_provider
        default_model = cls._default_model_for(provider)
        model = model_name or default_model

        return _LLMCacheKey(
            provider=provider,
            model=model,
            timeout=timeout,
            temperature=temperature,
            max_tokens=max_tokens,
            max_retries=max_retries,
            thinking_level=thinking_level,
        )

    @classmethod
    def _default_model_for(cls, provider: Provider) -> str:
        match provider:
            case Provider.GOOGLE:
                return cls.config.google_model
            case Provider.OLLAMA:
                return cls.config.ollama_model
            case Provider.OPENAI:
                return cls.config.openai_model
            case Provider.ANTHROPIC:
                return cls.config.anthropic_model
        assert_never(provider)

    @classmethod
    def _resolve_reasoning(cls, thinking_level: str) -> ReasoningLevel:
        levels = cls.config.reasoning_levels
        allowed_levels = ReasoningLevels.model_fields
        if thinking_level not in allowed_levels:
            allowed = ", ".join(sorted(allowed_levels))
            raise ValueError(
                f"Invalid thinking_level '{thinking_level}'. Allowed: {allowed}"
            )
        return getattr(levels, thinking_level)

    @classmethod
    def _create_llm(cls, key: _LLMCacheKey) -> BaseChatModel:
        reasoning = cls._resolve_reasoning(key.thinking_level)

        match key.provider:
            case Provider.GOOGLE:
                from langchain_google_genai import ChatGoogleGenerativeAI

                return ChatGoogleGenerativeAI(
                    model=key.model,
                    api_key=cls.config.google_api_key,
                    temperature=key.temperature,
                    max_tokens=key.max_tokens,
                    timeout=key.timeout,
                    max_retries=key.max_retries,
                    thinking_level=reasoning.google_level,
                )
            case Provider.OLLAMA:
                from langchain_ollama.chat_models import ChatOllama

                return ChatOllama(
                    model=key.model,
                    temperature=key.temperature,
                    num_predict=key.max_tokens,
                )
            case Provider.OPENAI:
                from langchain_openai import ChatOpenAI

                return ChatOpenAI(
                    model=key.model,
                    api_key=cls.config.openai_api_key,
                    temperature=key.temperature,
                    max_tokens=key.max_tokens,
                    timeout=key.timeout,
                    max_retries=key.max_retries,
                    reasoning_effort=reasoning.openai_effort,
                )
            case Provider.ANTHROPIC:
                from langchain_anthropic import ChatAnthropic

                return ChatAnthropic(
                    model=key.model,
                    api_key=cls.config.anthropic_api_key,
                    temperature=key.temperature,
                    max_tokens=key.max_tokens,
                    timeout=key.timeout,
                    max_retries=key.max_retries,
                    thinking={
                        "type": "enabled",
                        "budget_tokens": reasoning.claude_budget_tokens,
                    },
                )
        assert_never(key.provider)
