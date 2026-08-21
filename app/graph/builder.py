from langgraph.constants import END
from langgraph.graph import StateGraph

from app.graph.core.config import GraphState
from app.graph.nodes.start import start_node
from app.graph.nodes.temp import temp_node

base_builder = StateGraph(GraphState)
base_builder.set_entry_point("start")
base_builder.add_node("start", start_node)
base_builder.add_node("temp", temp_node)
base_builder.add_edge("start", "temp")
base_builder.add_edge("temp", END)
base_builder.set_finish_point("temp")
