from types import SimpleNamespace

import pytest

from app.services.llm.factory import LLMFactory


@pytest.fixture(autouse=True)
def clear_llm_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(LLMFactory, "_llms", {})


def test_get_llm_reuses_the_same_google_client(monkeypatch: pytest.MonkeyPatch) -> None:
    created_clients: list[object] = []

    class FakeGoogleClient:
        def __init__(self, **kwargs: object) -> None:
            self.kwargs = kwargs
            created_clients.append(self)

    config = SimpleNamespace(
        llm_provider="google",
        google_model="test-model",
        google_api_key="test-api-key",
        ollama_model="unused",
    )
    monkeypatch.setattr(LLMFactory, "config", config)
    monkeypatch.setattr(
        "app.services.llm.factory.ChatGoogleGenerativeAI", FakeGoogleClient
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

    config = SimpleNamespace(
        llm_provider="google",
        google_model="test-model",
        google_api_key="test-api-key",
        ollama_model="unused",
    )
    monkeypatch.setattr(LLMFactory, "config", config)
    monkeypatch.setattr(
        "app.services.llm.factory.ChatGoogleGenerativeAI", FakeGoogleClient
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

    config = SimpleNamespace(
        llm_provider="google",
        google_model="first-model",
        google_api_key="test-api-key",
        ollama_model="unused",
    )
    monkeypatch.setattr(LLMFactory, "config", config)
    monkeypatch.setattr(
        "app.services.llm.factory.ChatGoogleGenerativeAI", FakeGoogleClient
    )

    first_client = LLMFactory.get_llm(temperature=0.5)
    config.google_model = "second-model"
    second_client = LLMFactory.get_llm(temperature=0.5)

    assert first_client is not second_client
    assert len(created_clients) == 2
