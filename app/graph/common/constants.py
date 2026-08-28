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
