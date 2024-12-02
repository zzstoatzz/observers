from fastmcp import Context, FastMCP

from observers.github.source import check_notifications

# initialize fastmcp server
mcp = FastMCP(
    'notification observer',
    dependencies=[
        'observers[all]@git+https://github.com/zzstoatzz/observers.git'
    ],
)


@mcp.tool()
async def get_github_notifications(ctx: Context) -> list[dict]:
    """check github notifications

    returns a list of notification events from configured repositories
    """
    try:
        return [event.model_dump() for event in check_notifications()]
    except ValueError as e:
        # handle configuration errors
        ctx.error(str(e))
        return []
    except RuntimeError as e:
        # handle runtime errors
        ctx.error(str(e))
        return []


@mcp.prompt()
def analyze_notifications() -> str:
    return """analyze these github notifications and:
1. group by repository and type
2. identify urgent items needing attention
3. suggest next actions"""
