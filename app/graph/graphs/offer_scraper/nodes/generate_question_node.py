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
        description="Las keywords más importantes de la oferta de trabajo"
    )
    questions: list[str] = Field(
        description="Las preguntas más relevantes y útiles para la entrevista"
    )

    reasoning: str = Field(
        description="La razón por la que generaste las keywords y las preguntas"
    )

    summary: str = Field(description="El resumen de la oferta de trabajo")


def generate_question_node(state: GraphState):
    if not state.job_offer_context:
        return {
            GraphStateFields.ASSISTANT_MESSAGE: OFFER_CONTEXT_NOT_FOUND_MESSAGE,
            GraphStateFields.NODE_NAME: NodeNames.GENERATE_QUESTION_NODE,
            GraphStateFields.CONDITIONAL_EDGE: OfferScraperConstants.OFFER_CONTEXT_NOT_FOUND_EDGE,
        }

    model = LLMFactory.get_llm(
        timeout=20,
        temperature=1.4,
        max_tokens=1000,
        max_retries=3,
        thinking_level="low",
    )

    try:
        structured_model = model.with_structured_output(LLMOutput)
        ai_message = structured_model.invoke(
            QUESTION_GENERATOR_PROMPT.format(
                role=ROLE_PROMPT,
                question_numbers=10,
                job_offer=job_offer_to_markdown(state.job_offer_context),
            )
        )
    except Exception as e:
        get_logger(__name__).error(f"Error generating question: {e}")
        return {
            GraphStateFields.ASSISTANT_MESSAGE: GENERATE_QUESTION_ERROR_MESSAGE,
            GraphStateFields.NODE_NAME: NodeNames.GENERATE_QUESTION_NODE,
            GraphStateFields.CONDITIONAL_EDGE: OfferScraperConstants.GENERATE_QUESTION_ERROR_EDGE,
        }

    output = LLMOutput.model_validate(ai_message)

    first_question = output.questions[0]

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
        GraphStateFields.IS_TTS_MESSAGE: False,
    }
