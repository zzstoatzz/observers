# /// script
# dependencies = ["observers[all]@file://."]
# ///

from pathlib import Path
from typing import Any

from fastmcp import Context, FastMCP

from observers.github import GitHubEventFilter, GitHubObserver
from observers.gmail import GmailObserver
from observers.slack import SlackObserver

# Initialize FastMCP server
mcp = FastMCP(
    'Notification Observer',
    dependencies=[
        'google-auth-oauthlib',
        'google-auth-httplib2',
        'google-api-python-client',
        'slack_sdk',
        'httpx',
    ],
)

# Initialize observers (these would normally come from config)
gmail_observer = GmailObserver(creds_path=Path('credentials.json'), token_path=Path('token.json'))

github_observer = GitHubObserver(
    token='your-github-token',
    filters=[
        GitHubEventFilter(
            repositories=['user/repo'],
            event_types=['PullRequest', 'Issue'],
            reasons=['mention', 'review_requested'],
        )
    ],
)

slack_observer = SlackObserver(token='your-slack-token', lookback_hours=1)


@mcp.tool()
async def check_gmail(ctx: Context) -> list[dict[str, Any]]:
    """Check for new unread Gmail messages"""
    try:
        gmail_observer.connect()
        events = list(gmail_observer.observe())
        return [event.content for event in events]
    finally:
        gmail_observer.disconnect()


@mcp.tool()
async def check_github(ctx: Context) -> list[dict[str, Any]]:
    """Check for new GitHub notifications"""
    try:
        github_observer.connect()
        events = list(github_observer.observe())
        return [event.content for event in events]
    finally:
        github_observer.disconnect()


@mcp.tool()
async def check_slack(ctx: Context) -> list[dict[str, Any]]:
    """Check for new Slack messages"""
    try:
        slack_observer.connect()
        events = list(slack_observer.observe())
        return [event.content for event in events]
    finally:
        slack_observer.disconnect()


@mcp.tool()
async def check_all_notifications(ctx: Context) -> dict[str, list[dict[str, Any]]]:
    """Check notifications from all sources"""
    return {
        'gmail': await check_gmail(ctx),
        'github': await check_github(ctx),
        'slack': await check_slack(ctx),
    }


@mcp.prompt()
def analyze_notifications() -> str:
    return """Please analyze the notifications from different sources and:
1. Summarize the most important updates
2. Identify any urgent items that need attention
3. Group related notifications together
4. Suggest next actions based on the notifications"""


if __name__ == '__main__':
    mcp.run()
