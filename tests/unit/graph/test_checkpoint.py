from typing import Any, cast
from unittest.mock import patch

from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.base import CheckpointTuple
from langgraph.checkpoint.redis import RedisSaver

from app.graph.checkpoint import InterruptAwareRedisSaver


def test_get_tuple_restores_pending_interrupt_writes() -> None:
    config = cast(
        RunnableConfig,
        {
            "configurable": {
                "thread_id": "thread-1",
                "checkpoint_ns": "",
                "checkpoint_id": "checkpoint-1",
            }
        },
    )
    stored_tuple = CheckpointTuple(
        config=config,
        checkpoint=cast(Any, {}),
        metadata=cast(Any, {}),
        parent_config=None,
        pending_writes=[],
    )
    interrupt_write = cast(Any, ("task-1", "__interrupt__", ["question"]))
    saver = object.__new__(InterruptAwareRedisSaver)

    with (
        patch.object(RedisSaver, "get_tuple", return_value=stored_tuple),
        patch.object(
            InterruptAwareRedisSaver,
            "_load_pending_writes",
            return_value=[interrupt_write],
        ) as load_pending_writes,
    ):
        result = saver.get_tuple(config)

    assert result is not None
    assert result.pending_writes == [interrupt_write]
    load_pending_writes.assert_called_once_with(
        thread_id="thread-1",
        checkpoint_ns="",
        checkpoint_id="checkpoint-1",
    )
