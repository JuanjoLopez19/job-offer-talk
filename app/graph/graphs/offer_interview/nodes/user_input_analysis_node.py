from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from app.core.logger import get_logger
from app.graph.common.constants import GraphStateFields, NodeNames
from app.graph.core.config import GraphState
from app.graph.graphs.offer_interview.common.constants import OfferInterviewConstants
from app.graph.graphs.offer_interview.prompts.user_input_analysis_prompt import (
    USER_ANALYSIS_PROMPT,
)
from app.graph.graphs.offer_scraper.common.messages import (
    GENERATE_QUESTION_ERROR_MESSAGE,
    OFFER_CONTEXT_NOT_FOUND_MESSAGE,
)
from app.services.llm.factory import LLMFactory
from app.shared.tools import (
    add_msg_to_conversation_history,
    conversation_history_to_markdown,
)


class LlmOutput(BaseModel):
    output: str = Field(description="El mensaje de respuesta")
    next_node: str = Field(description="El nombre del nodo siguiente")
    reasoning: str = Field(
        description="El razonamiento de por qué la respuesta es correcta o no es correcta"
    )


def user_input_analysis_node(state: GraphState):
    if not state.job_offer_generated_info:
        return {
            GraphStateFields.ASSISTANT_MESSAGE: OFFER_CONTEXT_NOT_FOUND_MESSAGE,
            GraphStateFields.NODE_NAME: NodeNames.USER_INPUT_ANALYSIS_NODE,
            GraphStateFields.CONDITIONAL_EDGE: OfferInterviewConstants.OFFER_CONTEXT_NOT_FOUND_EDGE,
        }

    # TODO: Modify the model to use
    model = LLMFactory.get_llm(
        timeout=20,
        temperature=0.5,
        max_tokens=5000,
        max_retries=3,
        thinking_level="medium",
    )
    try:
        messages = [
            SystemMessage(
                content=USER_ANALYSIS_PROMPT.format(
                    question=state.assistant_message,
                    summary=state.job_offer_generated_info.get("summary", "No resumen"),
                    next_questions=state.job_offer_generated_info.get("questions", []),
                    conversation_history=conversation_history_to_markdown(
                        state.conversation_history
                    ),
                )
            ),
            HumanMessage(content=state.user_input),
        ]
        structured_model = model.with_structured_output(LlmOutput)
        ai_message = structured_model.invoke(messages)
    except Exception as e:
        get_logger(__name__).error(f"Error generating question: {e}")
        return {
            GraphStateFields.ASSISTANT_MESSAGE: GENERATE_QUESTION_ERROR_MESSAGE,
            GraphStateFields.NODE_NAME: NodeNames.USER_INPUT_ANALYSIS_NODE,
            GraphStateFields.CONDITIONAL_EDGE: OfferInterviewConstants.ANALYSIS_ERROR_EDGE,
        }

    output = LlmOutput.model_validate(ai_message)

    conversation_history = add_msg_to_conversation_history(
        "assistant", output.output, node_name=NodeNames.USER_INPUT_ANALYSIS_NODE
    )

    return {
        GraphStateFields.ASSISTANT_MESSAGE: output.output,
        GraphStateFields.NODE_NAME: NodeNames.USER_INPUT_ANALYSIS_NODE,
        GraphStateFields.CONDITIONAL_EDGE: output.next_node,
        GraphStateFields.IS_TTS_MESSAGE: False,
        GraphStateFields.CONVERSATION_HISTORY: conversation_history,
    }
