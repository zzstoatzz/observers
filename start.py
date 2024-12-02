from fastmcp import Context, FastMCP

from observers.github.source import check_notifications

# initialize fastmcp server
mcp = FastMCP(
    'notification observer',
    dependencies=['observers[all]'],
)


@mcp.tool()
async def get_github_notifications(ctx: Context) -> str:
    """check for new github notifications"""
    return str(check_notifications())


@mcp.prompt()
def analyze_notifications() -> str:
    return """analyze these github notifications and:
1. summarize the most important updates
2. identify any urgent items needing attention
3. group related notifications by repository
4. suggest next actions"""
