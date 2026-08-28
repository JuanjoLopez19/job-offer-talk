from threading import Lock
from typing import ClassVar

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama.chat_models import ChatOllama

from app.core.config import Config


class LLMFactory:
    config: ClassVar[Config] = Config()
    allowed_providers: ClassVar[list[str]] = ["google", "ollama"]
    _llm: ClassVar[ChatGoogleGenerativeAI | ChatOllama | None] = None
    _lock: ClassVar[Lock] = Lock()

    @classmethod
    def get_llm(cls) -> ChatGoogleGenerativeAI | ChatOllama:
        if cls._llm is None:
            with cls._lock:
                if cls._llm is None:
                    cls._llm = cls._create_llm()

        return cls._llm

    @classmethod
    def _create_llm(cls) -> ChatGoogleGenerativeAI | ChatOllama:
        if cls.config.llm_provider not in cls.allowed_providers:
            raise ValueError(f"Invalid LLM provider: {cls.config.llm_provider}")

        if cls.config.llm_provider == "google":
            return ChatGoogleGenerativeAI(
                model=cls.config.google_model,
                api_key=cls.config.google_api_key,
                temperature=1.0,  # Gemini 3.0+ defaults to 1.0
                max_tokens=None,
                timeout=None,
                max_retries=2,
            )

        return ChatOllama(model=cls.config.ollama_model)
