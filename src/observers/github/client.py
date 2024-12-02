from collections.abc import Generator
from typing import Self

import httpx

from observers.loggers import get_logger

from .types import GitHubEvent, GitHubEventFilter

logger = get_logger('observers.github')


class GitHubObserver:
    """github notification observer"""

    def __init__(
        self, token: str, filters: list[GitHubEventFilter] | None = None
    ):
        self.token = token
        self.filters = filters or []
        self.client = httpx.Client(
            headers={
                'Authorization': f'token {token}',
                'Accept': 'application/vnd.github.v3+json',
            }
        )

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_) -> None:
        self.client.close()

    def observe(self) -> Generator[GitHubEvent, None, None]:
        """get filtered github notifications"""
        try:
            response = self.client.get('https://api.github.com/notifications')
            if not 200 <= response.status_code < 300:
                logger.error(
                    f'failed to get notifications: {response.status_code}'
                )
                return

            for notification in response.json():
                # skip if doesn't match filters
                repo = notification['repository']['full_name']
                if self.filters and not any(
                    repo in f.repositories for f in self.filters
                ):
                    continue

                yield GitHubEvent(
                    id=notification['id'],
                    type=notification['subject']['type'],
                    title=notification['subject']['title'],
                    repository=repo,
                    reason=notification['reason'],
                    url=notification['subject']['url'],
                    raw=notification,
                )

        except Exception as e:
            logger.error(f'failed to get notifications: {e}')
            raise
