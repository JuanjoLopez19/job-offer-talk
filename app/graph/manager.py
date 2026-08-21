from dataclasses import dataclass, field
from typing import Any

from langfuse import Langfuse
from langfuse.langchain import CallbackHandler
from langgraph.checkpoint.redis import RedisSaver
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Command
from redis import Redis

from app.core.config import Config
from app.graph.builder import base_builder
from app.graph.core.config import GraphState
from app.shared.models import GraphInput


@dataclass(slots=True)
class GraphManager:
    checkpointer: RedisSaver = field(init=False)
    graph: CompiledStateGraph | None = None
    config: Config = field(default_factory=Config)
    langfuse: Langfuse = field(init=False)

    def __post_init__(self) -> None:
        self.langfuse = Langfuse(
            public_key=self.config.langfuse_public_key,
            secret_key=self.config.langfuse_secret_key,
            base_url=self.config.langfuse_base_url,
        )

    def compile_graph(self):
        self.checkpointer = self.__get_checkpointer()
        return base_builder.compile(checkpointer=self.checkpointer)

    def __get_checkpointer(self):
        client = Redis(host="localhost", port=6379, decode_responses=False)
        saver = RedisSaver(redis_client=client)
        saver.setup()
        return saver

    def __get_graph(self):
        if not self.graph:
            self.graph = self.compile_graph()
        return self.graph

    def __get_langfuse_callback(self) -> CallbackHandler:
        return CallbackHandler(public_key=self.config.langfuse_public_key)

    def invoke(self, graph_input: GraphInput, *, thread_id: str) -> Any:
        if not thread_id.strip():
            raise ValueError("thread_id cannot be empty")

        graph = self.__get_graph()
        config = {
            "configurable": {"thread_id": thread_id},
            "callbacks": [self.__get_langfuse_callback()],
        }

        snapshot = graph.get_state(config)
        print(snapshot)
        if snapshot.interrupts:
            return graph.invoke(Command(resume=graph_input.user_input), config=config)

        state = GraphState(**graph_input.model_dump())
        return graph.invoke(state, config=config)
