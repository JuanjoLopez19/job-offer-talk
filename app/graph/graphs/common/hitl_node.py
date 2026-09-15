from langgraph.types import interrupt

from app.graph.common.constants import GraphStateFields
from app.graph.core.config import GraphState
from app.shared.models import GraphResumeInput
from app.shared.tools import add_msg_to_conversation_history


def human_node(
    state: GraphState, node_name: str, *, add_to_conversation_history: bool = False
):
    user_input = interrupt(
        {
            GraphStateFields.ASSISTANT_MESSAGE: state.assistant_message,
            GraphStateFields.NODE_NAME: node_name,
        }
    )
    resume_value = (
        GraphResumeInput(user_input=user_input)
        if isinstance(user_input, str)
        else GraphResumeInput.model_validate(user_input)
    )
    if add_to_conversation_history:
        conversation_history = add_msg_to_conversation_history(
            "user", resume_value.user_input or "", node_name=node_name
        )
        return {
            GraphStateFields.USER_INPUT: resume_value.user_input,
            GraphStateFields.NODE_NAME: node_name,
            GraphStateFields.CONVERSATION_HISTORY: conversation_history,
            GraphStateFields.IS_TTS_ACTIVE: resume_value.is_tts_active,
        }
    else:
        return {
            GraphStateFields.USER_INPUT: resume_value.user_input,
            GraphStateFields.NODE_NAME: node_name,
            GraphStateFields.IS_TTS_ACTIVE: resume_value.is_tts_active,
        }
