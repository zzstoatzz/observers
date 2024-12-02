from typing import Any

from pydantic import BaseModel


class GitHubEventFilter(BaseModel):
    """filter for github notifications"""

    repositories: list[str]
    event_types: list[str] | None = None
    reasons: list[str] | None = None
    branch: str | None = None


class GitHubEvent(BaseModel):
    """github notification event"""

    id: str
    type: str
    title: str
    repository: str
    reason: str
    url: str | None = None
    raw: dict[str, Any]
