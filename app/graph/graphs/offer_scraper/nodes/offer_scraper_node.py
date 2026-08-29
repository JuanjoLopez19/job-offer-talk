from job_offer_scraper_mcp.scrapper.factory import FactoryScrapper
from pydantic_core import Url

from app.core.logger import get_logger
from app.graph.common.constants import GraphStateFields, NodeNames
from app.graph.core.config import GraphState
from app.graph.graphs.offer_scraper.common.constants import OfferScraperConstants
from app.graph.graphs.offer_scraper.common.messages import (
    EMPTY_INPUT_MESSAGE,
    INVALID_URL_MESSAGE,
    SCRAPING_COMPLETE_MESSAGE,
    SCRAPING_ERROR_MESSAGE,
)

logger = get_logger(__name__)


def offer_scraper_node(state: GraphState):
    last_user_input = state.user_input

    if last_user_input is None:
        return {
            GraphStateFields.ASSISTANT_MESSAGE: EMPTY_INPUT_MESSAGE,
            GraphStateFields.NODE_NAME: NodeNames.OFFER_SCRAPER_NODE,
            GraphStateFields.CONDITIONAL_EDGE: OfferScraperConstants.EMPTY_INPUT_EDGE,
        }

    try:
        url = Url(last_user_input)
    except ValueError:
        logger.error(f"Invalid URL: {last_user_input}")
        return {
            GraphStateFields.ASSISTANT_MESSAGE: INVALID_URL_MESSAGE,
            GraphStateFields.NODE_NAME: NodeNames.OFFER_SCRAPER_NODE,
            GraphStateFields.CONDITIONAL_EDGE: OfferScraperConstants.INVALID_URL_EDGE,
        }

    logger.info(f"Scraping process has been requested for URL: {url}")

    scraper = FactoryScrapper.get_scrapper(url)
    try:
        scraper.extract()
    except Exception as e:
        logger.error(f"Error during scraping process: {e}")
        return {
            GraphStateFields.ASSISTANT_MESSAGE: SCRAPING_ERROR_MESSAGE,
            GraphStateFields.NODE_NAME: NodeNames.OFFER_SCRAPER_NODE,
            GraphStateFields.CONDITIONAL_EDGE: (
                OfferScraperConstants.SCRAPING_ERROR_EDGE
            ),
        }

    info = scraper.get_job_offer_info()

    return {
        GraphStateFields.ASSISTANT_MESSAGE: SCRAPING_COMPLETE_MESSAGE,
        GraphStateFields.NODE_NAME: NodeNames.OFFER_SCRAPER_NODE,
        GraphStateFields.CONDITIONAL_EDGE: OfferScraperConstants.SCRAPING_COMPLETE_EDGE,
        GraphStateFields.JOB_OFFER_CONTEXT: info.model_dump(mode="json"),
    }
