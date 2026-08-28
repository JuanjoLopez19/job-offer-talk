from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.base import CheckpointTuple
from langgraph.checkpoint.redis import RedisSaver


class InterruptAwareRedisSaver(RedisSaver):
    """Restore pending writes omitted by RedisSaver's direct lookup path."""

    def get_tuple(self, config: RunnableConfig) -> CheckpointTuple | None:
        checkpoint_tuple = super().get_tuple(config)
        if checkpoint_tuple is None or checkpoint_tuple.pending_writes:
            return checkpoint_tuple

        configurable = checkpoint_tuple.config["configurable"]
        pending_writes = self._load_pending_writes(
            thread_id=configurable["thread_id"],
            checkpoint_ns=configurable.get("checkpoint_ns", ""),
            checkpoint_id=configurable["checkpoint_id"],
        )
        if not pending_writes:
            return checkpoint_tuple

        return CheckpointTuple(
            config=checkpoint_tuple.config,
            checkpoint=checkpoint_tuple.checkpoint,
            metadata=checkpoint_tuple.metadata,
            parent_config=checkpoint_tuple.parent_config,
            pending_writes=pending_writes,
        )
