from job_offer_scraper_mcp.scrapper.factory import FactoryScrapper
from pydantic_core import Url

from app.core.logger import get_logger
from app.graph.common.constants import NodeNames
from app.graph.core.config import GraphState

logger = get_logger(__name__)


def offer_scraper_node(state: GraphState):
    last_user_input = state.user_input

    if last_user_input is None:
        return {
            "assistant_message": "Please enter a valid URL",
            "node_name": NodeNames.OFFER_SCRAPER_NODE,
            "conditional_edge": "empty_input",
        }

    try:
        url = Url(last_user_input)
    except ValueError:
        logger.error(f"Invalid URL: {last_user_input}")
        return {
            "assistant_message": "Please enter a valid URL",
            "node_name": NodeNames.OFFER_SCRAPER_NODE,
            "conditional_edge": "invalid_url",
        }

    logger.info(f"Scraping process has been requested for URL: {url}")

    scraper = FactoryScrapper.get_scrapper(url)
    try:
        scraper.extract()
    except Exception as e:
        logger.error(f"Error during scraping process: {e}")
        return {
            "assistant_message": "An error occurred during the scraping process",
            "node_name": NodeNames.OFFER_SCRAPER_NODE,
            "conditional_edge": "scraping_error",
        }

    info = scraper.get_job_offer_info()

    return {
        "assistant_message": "The scraping process has been completed",
        "node_name": NodeNames.OFFER_SCRAPER_NODE,
        "conditional_edge": "scraping_complete",
        "job_offer_context": info.model_dump(),
    }
