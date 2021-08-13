import logging

from core.utils import get_latest_metrics

logger = logging.getLogger(__name__)


def metrics(request):
    try:
        return {"metrics": get_latest_metrics()}
    except Exception as e:
        logger.error(f"Failure loading metrics into template context: {e}")
