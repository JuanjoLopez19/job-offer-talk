from pydantic import BaseModel, Field

from app.core.logger import get_logger
from app.graph.common.constants import NodeNames
from app.graph.core.config import GraphState
from app.graph.graphs.offer_scraper.prompt.question_generator import (
    QUESTION_GENERATOR_PROMPT,
)
from app.services.llm.factory import LLMFactory


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


def generate_question_node(state: GraphState):
    if not state.job_offer_context:
        return {
            "assistant_message": "No job offer context found",
            "node_name": NodeNames.GENERATE_QUESTION_NODE,
            "conditional_edge": "error",
        }

    model = LLMFactory.get_llm()

    try:
        structured_model = model.with_structured_output(LLMOutput)
        ai_message = structured_model.invoke(
            QUESTION_GENERATOR_PROMPT.format(
                question_numbers=10, job_offer=state.job_offer_context
            )
        )
    except Exception as e:
        get_logger(__name__).error(f"Error generating question: {e}")
        return {
            "assistant_message": "An error occurred while generating the question. Please try again.",
            "node_name": NodeNames.GENERATE_QUESTION_NODE,
            "conditional_edge": "error",
        }

    output = LLMOutput.model_validate(ai_message)

    return {
        "assistant_message": output.questions[0],
        "job_offer_generated_info": output.model_dump(),
        "node_name": NodeNames.GENERATE_QUESTION_NODE,
        "conditional_edge": "success",
        "is_tts_message": True,
    }
