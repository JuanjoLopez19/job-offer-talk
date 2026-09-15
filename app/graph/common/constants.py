from enum import StrEnum

HITL_NODE_PREFIX = "hitl_node"


def build_hitl_node_name(node_name: str) -> str:
    return f"{node_name}_{HITL_NODE_PREFIX}"


class NodeNames:
    INITIAL_NODE = "start"
    INITIAL_HITL_NODE = build_hitl_node_name(INITIAL_NODE)

    URL_INPUT_NODE = "url_input_node"
    OFFER_SCRAPER_NODE = "offer_scraper_node"

    JOB_OFFER_PARSER_HITL_NODE = build_hitl_node_name(OFFER_SCRAPER_NODE)

    GENERATE_QUESTION_NODE = "generate_question_node"

    USER_INPUT_ANALYSIS_NODE = "user_input_analysis_node"
    USER_INPUT_ANALYSIS_HITL_NODE = build_hitl_node_name(USER_INPUT_ANALYSIS_NODE)

    ASK_FOR_NEW_QUESTION_NODE = "ask_for_new_question_node"
    ASK_FOR_NEW_QUESTION_HITL_NODE = build_hitl_node_name(ASK_FOR_NEW_QUESTION_NODE)


class GraphStateFields(StrEnum):
    SESSION_ID = "session_id"
    ASSISTANT_MESSAGE = "assistant_message"
    USER_INPUT = "user_input"
    NODE_NAME = "node_name"
    CONDITIONAL_EDGE = "conditional_edge"
    JOB_OFFER_CONTEXT = "job_offer_context"
    JOB_OFFER_GENERATED_INFO = "job_offer_generated_info"
    CONVERSATION_HISTORY = "conversation_history"
    IS_TTS_ACTIVE = "is_tts_active"
    COUNTER_QUESTIONS = "counter_questions"
