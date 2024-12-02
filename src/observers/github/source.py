from pathlib import Path
from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from observers.github.types import GitHubEvent
from observers.loggers import get_logger
from observers.settings import settings

from .client import GitHubObserver

logger = get_logger('observers.github')


class GitHubSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env', env_prefix='GITHUB_', extra='ignore'
    )

    enabled: bool = Field(default=False)
    token: str = Field(default=...)
    check_interval_seconds: int = Field(default=300)

    # use source-specific config dir
    event_filters_path: Path = Field(
        default=settings.app_dir / 'github' / 'filters.json'
    )

    def model_post_init(self, __context: Any) -> None:
        self.event_filters_path.parent.mkdir(parents=True, exist_ok=True)

        # write default filters if none exist
        if not self.event_filters_path.exists():
            self.event_filters_path.write_text("""[
    {
        "repositories": ["PrefectHQ/prefect"],
        "event_types": ["PullRequest", "Issue"],
        "reasons": ["subscribed", "review_requested", "mention"]
    },
    {
        "repositories": ["zzstoatzz/assistant"],
        "event_types": ["PullRequest", "Issue"],
        "reasons": [
            "subscribed", 
            "review_requested",
            "mention",
            "comment",
            "state_change",
            "assign",
            "author"
        ]
    }
]""")


github = GitHubSettings()


def check_notifications() -> list[GitHubEvent]:
    """check github notifications"""
    if not github.enabled:
        logger.info('github notifications disabled')
        raise ValueError('github notifications disabled')

    if not github.token:
        raise ValueError('github token not configured')

    try:
        with GitHubObserver(token=github.token) as observer:
            events = list(observer.observe())
            logger.info(f'found {len(events)} github notifications')
            return events
    except Exception as e:
        raise RuntimeError(f'failed to check notifications: {e}')
