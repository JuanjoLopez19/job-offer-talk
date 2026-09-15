from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from app.core.logger import get_logger
from app.graph.common.constants import GraphStateFields, NodeNames
from app.graph.core.config import GraphState
from app.graph.graphs.common.prompts.role_prompt import ROLE_PROMPT
from app.graph.graphs.offer_scraper.common.constants import OfferScraperConstants
from app.graph.graphs.offer_scraper.common.messages import (
    GENERATE_QUESTION_ERROR_MESSAGE,
    OFFER_CONTEXT_NOT_FOUND_MESSAGE,
)
from app.graph.graphs.offer_scraper.prompt.question_generator import (
    QUESTION_GENERATOR_PROMPT,
)
from app.services.llm.factory import LLMFactory
from app.shared.tools import add_msg_to_conversation_history, job_offer_to_markdown


class LLMOutput(BaseModel):
    keywords: list[str] = Field(
        description=(
            "Las palabras clave más importantes de la oferta. Conserva los nombres "
            "propios y de tecnologías en su idioma original."
        )
    )
    questions: list[str] = Field(
        description=(
            "Las preguntas más relevantes y útiles para la entrevista, redactadas "
            "íntegramente en español de España."
        ),
        min_length=1,
    )

    reasoning: str = Field(
        description=(
            "La razón por la que generaste las palabras clave y las preguntas, "
            "redactada íntegramente en español de España."
        )
    )

    summary: str = Field(
        description=(
            "El resumen de la oferta de trabajo, redactado íntegramente en español "
            "de España."
        )
    )


def generate_question_node(state: GraphState):
    if not state.job_offer_context:
        return {
            GraphStateFields.ASSISTANT_MESSAGE: OFFER_CONTEXT_NOT_FOUND_MESSAGE,
            GraphStateFields.NODE_NAME: NodeNames.GENERATE_QUESTION_NODE,
            GraphStateFields.CONDITIONAL_EDGE: OfferScraperConstants.OFFER_CONTEXT_NOT_FOUND_EDGE,
        }

    model = LLMFactory.get_llm(
        timeout=20,
        temperature=0.2,
        max_tokens=1000,
        max_retries=3,
        thinking_level="low",
    )

    try:
        structured_model = model.with_structured_output(LLMOutput)
        ai_message = structured_model.invoke(
            [
                SystemMessage(content=ROLE_PROMPT),
                HumanMessage(
                    content=QUESTION_GENERATOR_PROMPT.format(
                        question_numbers=10,
                        job_offer=job_offer_to_markdown(state.job_offer_context),
                    )
                ),
            ]
        )
        output = LLMOutput.model_validate(ai_message)
        first_question = output.questions[0]
    except Exception as e:
        get_logger(__name__).error(f"Error generating question: {e}")
        return {
            GraphStateFields.ASSISTANT_MESSAGE: GENERATE_QUESTION_ERROR_MESSAGE,
            GraphStateFields.NODE_NAME: NodeNames.GENERATE_QUESTION_NODE,
            GraphStateFields.CONDITIONAL_EDGE: OfferScraperConstants.GENERATE_QUESTION_ERROR_EDGE,
        }

    conversation_history = add_msg_to_conversation_history(
        "assistant", first_question, node_name=NodeNames.GENERATE_QUESTION_NODE
    )

    output.questions = output.questions[1:]
    return {
        GraphStateFields.ASSISTANT_MESSAGE: first_question,
        GraphStateFields.CONVERSATION_HISTORY: conversation_history,
        GraphStateFields.JOB_OFFER_GENERATED_INFO: output.model_dump(),
        GraphStateFields.NODE_NAME: NodeNames.GENERATE_QUESTION_NODE,
        GraphStateFields.CONDITIONAL_EDGE: OfferScraperConstants.GENERATE_QUESTION_SUCCESS_EDGE,
    }
