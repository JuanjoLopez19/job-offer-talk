from datetime import datetime
from typing import Any, Literal

from job_offer_scraper_mcp.shared.constants import JobOfferInfo


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
