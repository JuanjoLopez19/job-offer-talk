from datetime import datetime
from typing import Any, Literal

from bs4 import BeautifulSoup
from job_offer_scraper_mcp.shared.constants import JobOfferInfo

from app.graph.core.config import GraphState


def job_offer_to_markdown(job_offer: dict[str, Any]) -> str:
    item = JobOfferInfo.model_validate(job_offer)

    return f"""### Título
{item.title}    
### Empresa
{item.company_name}
### Tipo de contrato
{item.location}
### Descripción
{item.description}
### Criterios
{item.criteria}
"""


def add_msg_to_conversation_history(
    role: Literal["user", "assistant"], message: str, *, node_name: str
):
    return [
        {
            "role": role,
            "content": message,
            "timestamp": datetime.now().isoformat(),
            "node_name": node_name,
        }
    ]


def conversation_history_to_markdown(conversation_history: list[dict[str, Any]]) -> str:
    return "\n".join(
        [
            f"### {msg['role']} ({msg['timestamp']})\n{msg['content']}"
            for msg in conversation_history
        ]
    )


def remove_question_from_list(questions_list: list[str], question: str) -> list[str]:
    updated_questions = questions_list.copy()
    if question in updated_questions:
        updated_questions.remove(question)
    return updated_questions


def is_tts_response(response: GraphState) -> bool:
    return bool(
        response.is_tts_active
        and response.assistant_message
        and response.assistant_message.strip()
    )


def remove_html_tags(text: str) -> str:
    return BeautifulSoup(text, "html.parser").get_text()
