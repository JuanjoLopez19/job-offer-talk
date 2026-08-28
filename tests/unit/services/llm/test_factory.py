from types import SimpleNamespace

import pytest

from app.services.llm.factory import LLMFactory


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
    monkeypatch.setattr(LLMFactory, "_llm", None)
    monkeypatch.setattr(
        "app.services.llm.factory.ChatGoogleGenerativeAI", FakeGoogleClient
    )

    first_client = LLMFactory.get_llm()
    second_client = LLMFactory.get_llm()

    assert first_client is second_client
    assert len(created_clients) == 1
    assert isinstance(created_clients[0], FakeGoogleClient)
    assert created_clients[0].kwargs["model"] == "test-model"
