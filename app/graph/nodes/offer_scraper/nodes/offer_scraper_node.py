from app.graph.core.config import GraphState


def offer_scraper_node(state: GraphState):
    return {
        "assistant_message": "I am offering you a job",
        "node_name": "offer_scraper_node",
    }
