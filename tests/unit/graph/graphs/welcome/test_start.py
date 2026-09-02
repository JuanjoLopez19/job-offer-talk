from app.graph.common.constants import NodeNames
from app.graph.common.messages import WELCOME_MESSAGE
from app.graph.core.config import GraphState
from app.graph.graphs.welcome.nodes.start import start_node


def test_start_node_returns_the_welcome_message() -> None:
    result = start_node(GraphState(session_id="thread-1"))

    assert result["assistant_message"] == WELCOME_MESSAGE
    assert result["node_name"] == NodeNames.INITIAL_NODE
