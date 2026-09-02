from typing import Any, Literal

from langgraph.constants import END
from pydantic import BaseModel, Field

from app.core.logger import get_logger
from app.graph.common.constants import GraphStateFields, NodeNames
from app.graph.core.config import GraphState
from app.graph.graphs.common.prompts.role_prompt import ROLE_PROMPT
from app.graph.graphs.offer_interview.common.constants import OfferInterviewConstants
from app.graph.graphs.offer_interview.common.messages import (
    ENDING_WITHOUT_UNDERSTANDING_MESSAGE,
)
from app.graph.graphs.offer_interview.prompts.ask_new_question_prompt import (
    ASK_NEW_QUESTION_PROMPT,
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

    next_node: Literal[
        # pyrefly: ignore [invalid-literal]
        OfferInterviewConstants.CONTINUE_EDGE,
        # pyrefly: ignore [invalid-literal]
        OfferInterviewConstants.REPEAT_EDGE,
    ] = Field(description="El nombre del nodo siguiente")
    reasoning: str = Field(
        description="El razonamiento de por qué la respuesta es correcta o no es correcta"
    )
    question: str = Field(
        description="La pregunta sobre la que se le está preguntando o se le va a preguntar al usuario"
    )


def ask_for_new_question_node(state: GraphState):
    if not state.job_offer_generated_info:
        return {
            GraphStateFields.ASSISTANT_MESSAGE: OFFER_CONTEXT_NOT_FOUND_MESSAGE,
            GraphStateFields.NODE_NAME: NodeNames.ASK_FOR_NEW_QUESTION_NODE,
            GraphStateFields.CONDITIONAL_EDGE: OfferInterviewConstants.OFFER_CONTEXT_NOT_FOUND_EDGE,
        }

    updates: dict[GraphStateFields, Any] = {
        GraphStateFields.NODE_NAME: NodeNames.ASK_FOR_NEW_QUESTION_NODE,
        GraphStateFields.IS_TTS_MESSAGE: False,
    }

    try:
        model = LLMFactory.get_llm(
            timeout=10,
            temperature=0.5,
            max_tokens=1000,
            max_retries=3,
            thinking_level="minimal",
        )
        message = ASK_NEW_QUESTION_PROMPT.format(
            role=ROLE_PROMPT,
            question=state.assistant_message,
            next_questions=state.job_offer_generated_info.get("questions", []),
            conversation_history=conversation_history_to_markdown(
                state.conversation_history
            ),
        )

        structured_model = model.with_structured_output(LlmOutput)
        ai_message = structured_model.invoke(message)
    except Exception as e:
        get_logger(__name__).error(
            f"Error generating the analysis of the user input: {e}"
        )
        return {
            GraphStateFields.ASSISTANT_MESSAGE: GENERATE_QUESTION_ERROR_MESSAGE,
            GraphStateFields.NODE_NAME: NodeNames.ASK_FOR_NEW_QUESTION_NODE,
            GraphStateFields.CONDITIONAL_EDGE: OfferInterviewConstants.ANALYSIS_ERROR_EDGE,
        }

    output = LlmOutput.model_validate(ai_message)

    message = output.output

    updates[GraphStateFields.CONDITIONAL_EDGE] = output.next_node
    if output.next_node == OfferInterviewConstants.REPEAT_EDGE:
        updates[GraphStateFields.COUNTER_QUESTIONS] = state.counter_questions + 1
    else:
        updates[GraphStateFields.COUNTER_QUESTIONS] = 0

    if (
        updates[GraphStateFields.COUNTER_QUESTIONS]
        >= OfferInterviewConstants.MAX_DIALOG_ROUNDS_ASK_NEW_QUESTION
    ):
        get_logger(__name__).info("Max Counter Reached, ending the conversation")
        updates[GraphStateFields.COUNTER_QUESTIONS] = 0
        updates[GraphStateFields.CONDITIONAL_EDGE] = END
        message = ENDING_WITHOUT_UNDERSTANDING_MESSAGE

        conversation_history = add_msg_to_conversation_history(
            "assistant",
            message,
            node_name=NodeNames.ASK_FOR_NEW_QUESTION_NODE,
        )
    else:
        conversation_history = add_msg_to_conversation_history(
            "assistant", message, node_name=NodeNames.ASK_FOR_NEW_QUESTION_NODE
        )

    updates[GraphStateFields.CONVERSATION_HISTORY] = conversation_history
    return {
        **updates,
        GraphStateFields.ASSISTANT_MESSAGE: message,
    }
