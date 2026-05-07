"""MCP server with Steam tools for gaming library, achievements, and store search.

Tool return-type conventions:
- Data tools return real `dict` or `list[dict]` so FastMCP serializes them as
  proper structured content (no json.dumps wrapping).
- `resolve_vanity_url` returns a bare `str` (single ID value).
- Errors are raised as exceptions; FastMCP translates them into MCP error
  responses with `isError=true`.
"""

from importlib.metadata import PackageNotFoundError, version

from mcp.server.fastmcp import FastMCP

from .client import SteamClient

mcp = FastMCP("mcp-steam")


@mcp.tool()
def get_server_version() -> str:
    """Return the installed version of the mcp-steam server."""
    try:
        return version("mcp-steam")
    except PackageNotFoundError:
        return "unknown"


_client: SteamClient | None = None


def _get_client() -> SteamClient:
    global _client
    if _client is None:
        _client = SteamClient()
    return _client


# ---------------------------------------------------------------------------
# User Resolution
# ---------------------------------------------------------------------------


@mcp.tool()
def resolve_vanity_url(vanity_name: str) -> str:
    """Resolve a Steam vanity URL name to a 64-bit Steam ID.

    Converts a custom profile URL name (e.g. "gabelogannewell") into
    the numeric Steam ID needed by other tools. Useful when you only
    know someone's profile name.
    """
    return _get_client().resolve_vanity_url(vanity_name)


# ---------------------------------------------------------------------------
# Library
# ---------------------------------------------------------------------------


@mcp.tool()
def get_owned_games(sort_by: str = "playtime", limit: int = 50) -> list[dict]:
    """Get your Steam game library with playtime stats.

    sort_by options: "playtime" (default, most played first),
    "recent" (most recently played first), "name" (alphabetical).

    Returns game names, app IDs, and total/recent playtime.
    """
    return _get_client().get_owned_games(sort_by, limit)


@mcp.tool()
def get_recently_played(limit: int = 10) -> list[dict]:
    """Get your recently played Steam games (last 2 weeks).

    Returns game names, app IDs, and playtime for the period.
    """
    return _get_client().get_recently_played(limit)


# ---------------------------------------------------------------------------
# Game Info
# ---------------------------------------------------------------------------


@mcp.tool()
def get_game_details(app_id: str) -> dict:
    """Get detailed store information for a Steam game.

    Returns name, description, price, genres, platforms, metacritic
    score, and release date. Use the app_id from library or search results.
    """
    return _get_client().get_game_details(app_id)


@mcp.tool()
def search_games(query: str, limit: int = 10) -> list[dict]:
    """Search the Steam store for games.

    Returns game names, app IDs, prices, and supported platforms.
    """
    return _get_client().search_games(query, limit)


# ---------------------------------------------------------------------------
# Achievements & Stats
# ---------------------------------------------------------------------------


@mcp.tool()
def get_achievements(app_id: str) -> dict:
    """Get your achievement progress for a Steam game.

    Returns each achievement's unlock status, description, unlock time,
    and how rare it is globally. Includes unlocked/total summary.
    """
    return _get_client().get_achievements(app_id)


@mcp.tool()
def get_player_stats(app_id: str) -> dict:
    """Get your gameplay statistics for a Steam game.

    Returns game-specific stats like kills, deaths, time played, etc.
    Not all games provide stats.
    """
    return _get_client().get_player_stats(app_id)


@mcp.tool()
def get_global_achievement_stats(app_id: str) -> list[dict]:
    """Get global achievement unlock percentages for a Steam game.

    Shows how rare each achievement is across all players. Useful for
    identifying the hardest or rarest achievements.
    """
    return _get_client().get_global_achievement_stats(app_id)


# ---------------------------------------------------------------------------
# Wishlist
# ---------------------------------------------------------------------------


@mcp.tool()
def get_wishlist(limit: int = 50) -> list[dict]:
    """Get your Steam wishlist.

    Returns wishlisted games sorted by priority, with prices and
    current discounts if available.
    """
    return _get_client().get_wishlist(limit)


# ---------------------------------------------------------------------------
# News
# ---------------------------------------------------------------------------


@mcp.tool()
def get_game_news(app_id: str, count: int = 5) -> list[dict]:
    """Get recent news and updates for a Steam game.

    Returns news titles, authors, dates, summaries, and URLs.
    """
    return _get_client().get_game_news(app_id, count)


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------


@mcp.tool()
def get_player_summary(steam_id: str = "") -> dict:
    """Get a Steam profile summary.

    Returns display name, online status, profile URL, and currently
    playing game (if any).

    steam_id: optional Steam ID or vanity name. Defaults to your own profile.
    """
    return _get_client().get_player_summary(steam_id or None)


@mcp.tool()
def get_friend_list(steam_id: str = "") -> list[dict]:
    """Get a Steam friends list.

    Returns friend Steam IDs, relationship status, and when you
    became friends.

    steam_id: optional Steam ID or vanity name. Defaults to your own profile.
    """
    return _get_client().get_friend_list(steam_id or None)


# ---------------------------------------------------------------------------
# Player Info
# ---------------------------------------------------------------------------


@mcp.tool()
def get_player_bans(steam_id: str = "") -> dict:
    """Get ban status for a Steam player.

    Returns VAC bans, community bans, game bans, and trade/economy ban status.

    steam_id: optional Steam ID or vanity name. Defaults to your own profile.
    """
    return _get_client().get_player_bans(steam_id or None)


@mcp.tool()
def get_steam_level(steam_id: str = "") -> dict:
    """Get the Steam level for a player.

    steam_id: optional Steam ID or vanity name. Defaults to your own profile.
    """
    return _get_client().get_steam_level(steam_id or None)


# ---------------------------------------------------------------------------
# Game Info (continued)
# ---------------------------------------------------------------------------


@mcp.tool()
def get_current_players(app_id: str) -> dict:
    """Get the current number of players in a Steam game.

    Returns the live concurrent player count.
    """
    return _get_client().get_current_players(app_id)


@mcp.tool()
def get_game_schema(app_id: str) -> dict:
    """Get achievement and stat definitions for a Steam game.

    Returns achievement display names, descriptions, and hidden status,
    plus stat definitions. Useful for understanding what stats and
    achievements a game tracks.
    """
    return _get_client().get_game_schema(app_id)


# ---------------------------------------------------------------------------
# Store Discovery
# ---------------------------------------------------------------------------


@mcp.tool()
def get_app_reviews(
    app_id: str,
    review_type: str = "all",
    limit: int = 10,
) -> dict:
    """Get user reviews for a Steam game.

    Returns review text, recommendation, playtime, and helpfulness votes.
    Includes summary with total positive/negative counts and score description.

    review_type: "all" (default), "positive", or "negative".
    """
    return _get_client().get_app_reviews(app_id, review_type, limit)


@mcp.tool()
def get_featured_categories() -> dict:
    """Get Steam store featured categories.

    Returns games organized by category: Top Sellers, New Releases,
    Specials, Coming Soon, and more. Each category includes game names,
    prices, and discounts.
    """
    return _get_client().get_featured_categories()


@mcp.tool()
def get_package_details(package_id: str) -> dict:
    """Get details for a Steam package or bundle.

    Returns package name, price, discount, included apps, platforms,
    and release date. Use for bundles and multi-game packages.
    """
    return _get_client().get_package_details(package_id)


# ---------------------------------------------------------------------------
# Featured
# ---------------------------------------------------------------------------


@mcp.tool()
def get_featured_games() -> dict:
    """Get currently featured and on-sale games on Steam.

    Returns featured games split into on-sale (with discounts and prices)
    and regular featured titles.
    """
    return _get_client().get_featured_games()
