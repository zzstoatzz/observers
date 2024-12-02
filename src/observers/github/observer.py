from typing import Any

from pydantic import TypeAdapter

from observers.loggers import get_logger

from .source import github
from .types import GitHubEventFilter

logger = get_logger('observers.github.observer')


def load_filters() -> list[GitHubEventFilter]:
    """load github event filters from json file"""
    if not github.event_filters_path.exists():
        logger.warning(f'no filters file at {github.event_filters_path}')
        return []

    try:
        return TypeAdapter(list[GitHubEventFilter]).validate_json(
            github.event_filters_path.read_text()
        )
    except Exception as e:
        logger.error(f'failed to load filters: {e}')
        return []


def filter_event(
    event: dict[str, Any], filters: list[GitHubEventFilter]
) -> bool:
    """check if event matches any filter"""
    if not filters:
        return True

    for f in filters:
        if event['repository'] not in f.repositories:
            continue

        if f.event_types and event['type'] not in f.event_types:
            continue

        if f.reasons and event['reason'] not in f.reasons:
            continue

        # matched all criteria
        return True

    return False
