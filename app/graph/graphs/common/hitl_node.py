from langgraph.types import interrupt

from app.graph.common.constants import GraphStateFields
from app.graph.core.config import GraphState
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

    if add_to_conversation_history:
        conversation_history = add_msg_to_conversation_history(
            "user", user_input, node_name=node_name
        )
        return {
            GraphStateFields.USER_INPUT: user_input,
            GraphStateFields.NODE_NAME: node_name,
            GraphStateFields.CONVERSATION_HISTORY: conversation_history,
        }
    else:
        return {
            GraphStateFields.USER_INPUT: user_input,
            GraphStateFields.NODE_NAME: node_name,
        }
