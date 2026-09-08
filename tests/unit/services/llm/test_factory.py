from types import SimpleNamespace

import pytest

from app.core.config import Provider, ReasoningLevel, ReasoningLevels
from app.services.llm.factory import LLMFactory


def _reasoning_levels() -> ReasoningLevels:
    return ReasoningLevels(
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


@pytest.fixture(autouse=True)
def clear_llm_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(LLMFactory, "_llms", {})


def _google_config(monkeypatch: pytest.MonkeyPatch) -> None:
    config = SimpleNamespace(
        llm_provider=Provider.GOOGLE,
        google_model="test-model",
        google_api_key="test-api-key",
        ollama_model="unused",
        openai_model="unused",
        anthropic_model="unused",
        openai_api_key=None,
        anthropic_api_key=None,
        reasoning_levels=_reasoning_levels(),
    )
    monkeypatch.setattr(LLMFactory, "config", config)


def test_get_llm_reuses_the_same_google_client(monkeypatch: pytest.MonkeyPatch) -> None:
    created_clients: list[object] = []

    class FakeGoogleClient:
        def __init__(self, **kwargs: object) -> None:
            self.kwargs = kwargs
            created_clients.append(self)

    _google_config(monkeypatch)
    monkeypatch.setattr(
        "langchain_google_genai.ChatGoogleGenerativeAI", FakeGoogleClient
    )

    first_client = LLMFactory.get_llm()
    second_client = LLMFactory.get_llm()

    assert first_client is second_client
    assert len(created_clients) == 1
    assert isinstance(created_clients[0], FakeGoogleClient)
    assert created_clients[0].kwargs["model"] == "test-model"


def test_get_llm_caches_google_clients_by_hyperparameters(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeGoogleClient:
        def __init__(self, **kwargs: object) -> None:
            self.kwargs = kwargs
            created_clients.append(self)

    created_clients: list[FakeGoogleClient] = []

    _google_config(monkeypatch)
    monkeypatch.setattr(
        "langchain_google_genai.ChatGoogleGenerativeAI", FakeGoogleClient
    )

    creative_client = LLMFactory.get_llm(temperature=1.4, thinking_level="low")
    analysis_client = LLMFactory.get_llm(temperature=0.5, thinking_level="medium")
    reused_analysis_client = LLMFactory.get_llm(
        temperature=0.5, thinking_level="medium"
    )

    assert creative_client is not analysis_client
    assert analysis_client is reused_analysis_client
    assert len(created_clients) == 2
    assert created_clients[0].kwargs["temperature"] == 1.4
    assert created_clients[1].kwargs["temperature"] == 0.5
    assert created_clients[1].kwargs["thinking_level"] == "medium"


def test_get_llm_caches_google_clients_by_model(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    created_clients: list[object] = []

    class FakeGoogleClient:
        def __init__(self, **kwargs: object) -> None:
            created_clients.append(self)

    _google_config(monkeypatch)
    monkeypatch.setattr(
        "langchain_google_genai.ChatGoogleGenerativeAI", FakeGoogleClient
    )

    first_client = LLMFactory.get_llm(temperature=0.5)
    LLMFactory.config.google_model = "second-model"  # type: ignore[attr-defined]
    second_client = LLMFactory.get_llm(temperature=0.5)

    assert first_client is not second_client
    assert len(created_clients) == 2


def test_get_llm_rejects_invalid_thinking_level_before_creating_client(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _google_config(monkeypatch)

    with pytest.raises(ValueError, match="Invalid thinking_level 'invalid'.*"):
        LLMFactory.get_llm(thinking_level="invalid")


def test_get_llm_translates_thinking_level_for_openai(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    created_clients: list[object] = []

    class FakeOpenAIClient:
        def __init__(self, **kwargs: object) -> None:
            self.kwargs = kwargs
            created_clients.append(self)

    config = SimpleNamespace(
        llm_provider=Provider.OPENAI,
        google_model="unused",
        ollama_model="unused",
        openai_model="test-openai-model",
        anthropic_model="unused",
        openai_api_key="test-openai-key",
        anthropic_api_key=None,
        reasoning_levels=_reasoning_levels(),
    )
    monkeypatch.setattr(LLMFactory, "config", config)
    monkeypatch.setattr("langchain_openai.ChatOpenAI", FakeOpenAIClient)

    default_client = LLMFactory.get_llm(thinking_level="high")
    named_client = LLMFactory.get_llm(model_name="gpt-4o", thinking_level="high")

    assert isinstance(default_client, FakeOpenAIClient)
    assert default_client.kwargs["model"] == "test-openai-model"
    assert default_client.kwargs["reasoning_effort"] == "high"
    assert isinstance(named_client, FakeOpenAIClient)
    assert named_client.kwargs["model"] == "gpt-4o"


def test_get_llm_translates_thinking_level_for_anthropic(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    created_clients: list[object] = []

    class FakeAnthropicClient:
        def __init__(self, **kwargs: object) -> None:
            self.kwargs = kwargs
            created_clients.append(self)

    config = SimpleNamespace(
        llm_provider=Provider.ANTHROPIC,
        google_model="unused",
        ollama_model="unused",
        openai_model="unused",
        anthropic_model="test-anthropic-model",
        openai_api_key=None,
        anthropic_api_key="test-anthropic-key",
        reasoning_levels=_reasoning_levels(),
    )
    monkeypatch.setattr(LLMFactory, "config", config)
    monkeypatch.setattr("langchain_anthropic.ChatAnthropic", FakeAnthropicClient)

    default_client = LLMFactory.get_llm(thinking_level="medium")
    named_client = LLMFactory.get_llm(
        model_name="claude-3-opus", thinking_level="medium"
    )

    assert isinstance(default_client, FakeAnthropicClient)
    assert default_client.kwargs["model"] == "test-anthropic-model"
    assert default_client.kwargs["thinking"] == {
        "type": "enabled",
        "budget_tokens": 8192,
    }
    assert isinstance(named_client, FakeAnthropicClient)
    assert named_client.kwargs["model"] == "claude-3-opus"
