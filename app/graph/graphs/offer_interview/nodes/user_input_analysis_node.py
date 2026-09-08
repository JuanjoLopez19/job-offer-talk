from typing import Any, Literal

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from app.core.logger import get_logger
from app.graph.common.constants import GraphStateFields, NodeNames
from app.graph.core.config import GraphState
from app.graph.graphs.common.prompts.role_prompt import ROLE_PROMPT
from app.graph.graphs.offer_interview.common.constants import OfferInterviewConstants
from app.graph.graphs.offer_interview.prompts.message_generator_prompt import (
    MESSAGE_GENERATOR_PROMPT,
)
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
    remove_question_from_list,
)


class LlmOutput(BaseModel):
    output: str = Field(description="El mensaje de respuesta")

    next_node: Literal[
        # pyrefly: ignore [invalid-literal]
        OfferInterviewConstants.NEXT_QUESTION_EDGE,
        # pyrefly: ignore [invalid-literal]
        OfferInterviewConstants.NOT_COMPLETE_AND_COHERENT_EDGE,
        # pyrefly: ignore [invalid-literal]
        OfferInterviewConstants.NOT_IN_CONTEXT_EDGE,
        # pyrefly: ignore [invalid-literal]
        OfferInterviewConstants.NOT_CORRECT_EDGE,
        # pyrefly: ignore [invalid-literal]
        OfferInterviewConstants.END_EDGE,
    ] = Field(description="El nombre del nodo siguiente")
    reasoning: str = Field(
        description="El razonamiento de por qué la respuesta es correcta o no es correcta"
    )
    question: str = Field(
        description="La pregunta sobre la que se le está preguntando o se le va a preguntar al usuario"
    )


class MessageGeneratorOutput(BaseModel):
    output: str = Field(description="El mensaje de respuesta")
    question: str = Field(
        description="La pregunta actual de las preguntas disponibles que se debe preguntar al usuario, exactamente igual al valor de la clave de la lista 'next_questions'"
    )


def user_input_analysis_node(state: GraphState):
    if not state.job_offer_generated_info:
        return {
            GraphStateFields.ASSISTANT_MESSAGE: OFFER_CONTEXT_NOT_FOUND_MESSAGE,
            GraphStateFields.NODE_NAME: NodeNames.USER_INPUT_ANALYSIS_NODE,
            GraphStateFields.CONDITIONAL_EDGE: OfferInterviewConstants.OFFER_CONTEXT_NOT_FOUND_EDGE,
        }

    updates: dict[GraphStateFields, Any] = {
        GraphStateFields.NODE_NAME: NodeNames.USER_INPUT_ANALYSIS_NODE,
    }

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
                    role=ROLE_PROMPT,
                    question=state.assistant_message,
                    summary=state.job_offer_generated_info.get(
                        "summary", "No resumen existente"
                    ),
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
        get_logger(__name__).error(
            f"Error generating the analysis of the user input: {e}"
        )
        return {
            GraphStateFields.ASSISTANT_MESSAGE: GENERATE_QUESTION_ERROR_MESSAGE,
            GraphStateFields.NODE_NAME: NodeNames.USER_INPUT_ANALYSIS_NODE,
            GraphStateFields.CONDITIONAL_EDGE: OfferInterviewConstants.ANALYSIS_ERROR_EDGE,
        }

    output = LlmOutput.model_validate(ai_message)

    if output.next_node in [
        OfferInterviewConstants.NEXT_QUESTION_EDGE,
        OfferInterviewConstants.NOT_CORRECT_EDGE,
        OfferInterviewConstants.END_EDGE,
    ]:
        assistant_message = output.output
        conversation_history = add_msg_to_conversation_history(
            "assistant", output.output, node_name=NodeNames.USER_INPUT_ANALYSIS_NODE
        )
        updates[GraphStateFields.COUNTER_QUESTIONS] = 0
        if output.next_node == OfferInterviewConstants.NEXT_QUESTION_EDGE:
            offer_generated_info = {
                **state.job_offer_generated_info,
                "questions": remove_question_from_list(
                    state.job_offer_generated_info["questions"], output.question
                ),
            }
            updates[GraphStateFields.JOB_OFFER_GENERATED_INFO] = offer_generated_info
    else:
        updates[GraphStateFields.COUNTER_QUESTIONS] = state.counter_questions + 1

        if (
            updates[GraphStateFields.COUNTER_QUESTIONS]
            > OfferInterviewConstants.MAX_DIALOG_ROUNDS
        ):
            get_logger(__name__).info("Max Counter Reached, generating new message")
            updates[GraphStateFields.COUNTER_QUESTIONS] = 0
            message_prompt = MESSAGE_GENERATOR_PROMPT.format(
                role=ROLE_PROMPT,
                question=state.assistant_message,
                next_questions=state.job_offer_generated_info.get("questions", []),
                next_node=output.next_node,
            )

            model = LLMFactory.get_llm(
                timeout=10,
                temperature=1,
                max_tokens=1500,
                max_retries=3,
                thinking_level="low",
            )
            try:
                structured_model = model.with_structured_output(MessageGeneratorOutput)
                ai_message = structured_model.invoke(message_prompt)
            except Exception as e:
                get_logger(__name__).error(
                    f"Error generating the message for the user: {e}"
                )
                return {
                    GraphStateFields.ASSISTANT_MESSAGE: GENERATE_QUESTION_ERROR_MESSAGE,
                    GraphStateFields.NODE_NAME: NodeNames.USER_INPUT_ANALYSIS_NODE,
                    GraphStateFields.CONDITIONAL_EDGE: OfferInterviewConstants.ANALYSIS_ERROR_EDGE,
                }

            message_output = MessageGeneratorOutput.model_validate(ai_message)
            conversation_history = add_msg_to_conversation_history(
                "assistant",
                message_output.output,
                node_name=NodeNames.USER_INPUT_ANALYSIS_NODE,
            )
            assistant_message = message_output.output
            offer_generated_info = {
                **state.job_offer_generated_info,
                "questions": remove_question_from_list(
                    state.job_offer_generated_info["questions"],
                    message_output.question,
                ),
            }
            updates[GraphStateFields.JOB_OFFER_GENERATED_INFO] = offer_generated_info
        else:
            conversation_history = add_msg_to_conversation_history(
                "assistant", output.output, node_name=NodeNames.USER_INPUT_ANALYSIS_NODE
            )
            assistant_message = output.output
    return {
        **updates,
        GraphStateFields.ASSISTANT_MESSAGE: assistant_message,
        GraphStateFields.CONDITIONAL_EDGE: output.next_node,
        GraphStateFields.CONVERSATION_HISTORY: conversation_history,
    }
