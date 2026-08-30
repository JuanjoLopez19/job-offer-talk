from datetime import datetime

from job_offer_scraper_mcp.shared.constants import JobOfferInfo

from app.shared.tools import (
    add_msg_to_conversation_history,
    conversation_history_to_markdown,
    job_offer_to_markdown,
    remove_question_from_list,
)


def _job_offer() -> dict[str, object]:
    return JobOfferInfo(
        url="https://example.com/job",
        title="Backend Engineer",
        company_name="Example",
        location="Madrid",
        description="Construir servicios.",
        criteria="Python",
    ).model_dump(mode="json")


def test_job_offer_to_markdown_includes_the_relevant_fields() -> None:
    markdown = job_offer_to_markdown(_job_offer())

    assert "Backend Engineer" in markdown
    assert "Example" in markdown
    assert "Python" in markdown


def test_add_msg_to_conversation_history_returns_a_graph_update() -> None:
    history = add_msg_to_conversation_history("assistant", "Hola", node_name="start")

    assert history[0]["role"] == "assistant"
    assert history[0]["content"] == "Hola"
    assert history[0]["node_name"] == "start"
    datetime.fromisoformat(history[0]["timestamp"])


def test_conversation_history_to_markdown_preserves_message_order() -> None:
    markdown = conversation_history_to_markdown(
        [
            {
                "role": "assistant",
                "timestamp": "2026-01-01T10:00:00",
                "content": "Hola",
            },
            {"role": "user", "timestamp": "2026-01-01T10:01:00", "content": "Gracias"},
        ]
    )

    assert markdown.index("Hola") < markdown.index("Gracias")


def test_remove_question_from_list_removes_only_the_requested_question() -> None:
    questions = ["Pregunta 1", "Pregunta 2"]

    result = remove_question_from_list(questions, "Pregunta 1")

    assert result == ["Pregunta 2"]
    assert remove_question_from_list(result, "missing") == ["Pregunta 2"]
