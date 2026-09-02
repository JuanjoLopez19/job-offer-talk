from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from langfuse import Langfuse, propagate_attributes
from langfuse.langchain import CallbackHandler
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Command
from redis import Redis

from app.core.config import Config
from app.graph.builder import base_builder
from app.graph.checkpoint import InterruptAwareRedisSaver
from app.graph.core.config import GraphState
from app.shared.models import GraphInput


@dataclass(slots=True)
class GraphManager:
    checkpointer: InterruptAwareRedisSaver = field(init=False)
    graph: CompiledStateGraph | None = None
    config: Config = field(default_factory=Config)
    langfuse: Langfuse = field(init=False)
    graph_output_path: Path = Path("graph.png")

    def __post_init__(self) -> None:
        self.langfuse = Langfuse(
            public_key=self.config.langfuse_public_key,
            secret_key=self.config.langfuse_secret_key,
            base_url=self.config.langfuse_base_url,
            environment=self.config.environment,
            release=self.config.version,
        )

    def compile_graph(self):
        self.checkpointer = self.__get_checkpointer()
        return base_builder.compile(checkpointer=self.checkpointer)

    def __get_checkpointer(self):
        client = Redis.from_url(url=str(self.config.redis.url), decode_responses=False)
        saver = InterruptAwareRedisSaver(
            redis_client=client,
            ttl={"default_ttl": 3600},
        )
        saver.setup()
        return saver

    def export_graph(self, path: Path | None = None) -> Path:
        """Write a Mermaid diagram without relying on a remote rendering service."""
        graph = self.__get_graph(export=False)
        output_path = path or self.graph_output_path
        output_path.write_bytes(graph.get_graph().draw_mermaid_png())
        return output_path

    def __get_graph(self, *, export: bool = True):
        if not self.graph:
            self.graph = self.compile_graph()
            if export:
                self.export_graph()
        return self.graph

    def __get_langfuse_callback(self) -> CallbackHandler:
        return CallbackHandler(public_key=self.config.langfuse_public_key)

    def invoke(self, graph_input: GraphInput | str | dict[str, Any], *, thread_id: str):
        if not thread_id.strip():
            raise ValueError("thread_id cannot be empty")

        graph = self.__get_graph(export=True)
        config = {
            "configurable": {"thread_id": thread_id},
            "callbacks": [self.__get_langfuse_callback()],
            "metadata": {"langfuse_session_id": thread_id},
            "run_name": "JobTalk",
        }

        with propagate_attributes(
            trace_name=self.config.langfuse_trace_name,
            session_id=thread_id,
            tags=["JobTalk", "langgraph"],
            metadata={
                "environment": self.config.environment,
                "framework": "langgraph",
                "version": self.config.version,
            },
        ):
            snapshot = graph.get_state(config)
            if snapshot.interrupts:
                resume_value = (
                    graph_input.user_input
                    if isinstance(graph_input, GraphInput)
                    else graph_input
                )
                state = graph.invoke(Command(resume=resume_value), config=config)
                return GraphState.model_validate(state)

            if isinstance(graph_input, str):
                raise ValueError("initial graph input must be an object")

            input_data = (
                graph_input.model_dump()
                if isinstance(graph_input, GraphInput)
                else graph_input
            )
            state = {**input_data, "session_id": thread_id}
            state = graph.invoke(state, config=config)
            return GraphState.model_validate(state)
