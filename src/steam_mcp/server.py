"""MCP server with Steam tools for gaming library, achievements, and store search."""

import json

from mcp.server.fastmcp import FastMCP

from .client import SteamClient, SteamError

mcp = FastMCP("mcp-steam")

_client: SteamClient | None = None


def _get_client() -> SteamClient:
    global _client
    if _client is None:
        _client = SteamClient()
    return _client


# ---------------------------------------------------------------------------
# Library
# ---------------------------------------------------------------------------


@mcp.tool()
def get_owned_games(sort_by: str = "playtime", limit: int = 50) -> str:
    """Get your Steam game library with playtime stats.

    sort_by options: "playtime" (default, most played first),
    "recent" (most recently played first), "name" (alphabetical).

    Returns game names, app IDs, and total/recent playtime.
    """
    try:
        results = _get_client().get_owned_games(sort_by, limit)
        return json.dumps(results, indent=2)
    except (SteamError, ValueError) as e:
        return f"Error: {e}"


@mcp.tool()
def get_recently_played(limit: int = 10) -> str:
    """Get your recently played Steam games (last 2 weeks).

    Returns game names, app IDs, and playtime for the period.
    """
    try:
        results = _get_client().get_recently_played(limit)
        return json.dumps(results, indent=2)
    except (SteamError, ValueError) as e:
        return f"Error: {e}"


# ---------------------------------------------------------------------------
# Game Info
# ---------------------------------------------------------------------------


@mcp.tool()
def get_game_details(app_id: str) -> str:
    """Get detailed store information for a Steam game.

    Returns name, description, price, genres, platforms, metacritic
    score, and release date. Use the app_id from library or search results.
    """
    try:
        result = _get_client().get_game_details(app_id)
        return json.dumps(result, indent=2)
    except (SteamError, ValueError) as e:
        return f"Error: {e}"


@mcp.tool()
def search_games(query: str, limit: int = 10) -> str:
    """Search the Steam store for games.

    Returns game names, app IDs, prices, and supported platforms.
    """
    try:
        results = _get_client().search_games(query, limit)
        return json.dumps(results, indent=2)
    except (SteamError, ValueError) as e:
        return f"Error: {e}"


# ---------------------------------------------------------------------------
# Achievements & Stats
# ---------------------------------------------------------------------------


@mcp.tool()
def get_achievements(app_id: str) -> str:
    """Get your achievement progress for a Steam game.

    Returns each achievement's unlock status, description, unlock time,
    and how rare it is globally. Includes unlocked/total summary.
    """
    try:
        result = _get_client().get_achievements(app_id)
        return json.dumps(result, indent=2)
    except (SteamError, ValueError) as e:
        return f"Error: {e}"


@mcp.tool()
def get_player_stats(app_id: str) -> str:
    """Get your gameplay statistics for a Steam game.

    Returns game-specific stats like kills, deaths, time played, etc.
    Not all games provide stats.
    """
    try:
        result = _get_client().get_player_stats(app_id)
        return json.dumps(result, indent=2)
    except (SteamError, ValueError) as e:
        return f"Error: {e}"


@mcp.tool()
def get_global_achievement_stats(app_id: str) -> str:
    """Get global achievement unlock percentages for a Steam game.

    Shows how rare each achievement is across all players. Useful for
    identifying the hardest or rarest achievements.
    """
    try:
        results = _get_client().get_global_achievement_stats(app_id)
        return json.dumps(results, indent=2)
    except (SteamError, ValueError) as e:
        return f"Error: {e}"


# ---------------------------------------------------------------------------
# Wishlist
# ---------------------------------------------------------------------------


@mcp.tool()
def get_wishlist(limit: int = 50) -> str:
    """Get your Steam wishlist.

    Returns wishlisted games sorted by priority, with prices and
    current discounts if available.
    """
    try:
        results = _get_client().get_wishlist(limit)
        return json.dumps(results, indent=2)
    except (SteamError, ValueError) as e:
        return f"Error: {e}"


# ---------------------------------------------------------------------------
# News
# ---------------------------------------------------------------------------


@mcp.tool()
def get_game_news(app_id: str, count: int = 5) -> str:
    """Get recent news and updates for a Steam game.

    Returns news titles, authors, dates, summaries, and URLs.
    """
    try:
        results = _get_client().get_game_news(app_id, count)
        return json.dumps(results, indent=2)
    except (SteamError, ValueError) as e:
        return f"Error: {e}"


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------


@mcp.tool()
def get_player_summary() -> str:
    """Get your Steam profile summary.

    Returns display name, online status, profile URL, and currently
    playing game (if any).
    """
    try:
        result = _get_client().get_player_summary()
        return json.dumps(result, indent=2)
    except (SteamError, ValueError) as e:
        return f"Error: {e}"


@mcp.tool()
def get_friend_list() -> str:
    """Get your Steam friends list.

    Returns friend Steam IDs, relationship status, and when you
    became friends.
    """
    try:
        results = _get_client().get_friend_list()
        return json.dumps(results, indent=2)
    except (SteamError, ValueError) as e:
        return f"Error: {e}"


# ---------------------------------------------------------------------------
# Featured
# ---------------------------------------------------------------------------


@mcp.tool()
def get_featured_games() -> str:
    """Get currently featured and on-sale games on Steam.

    Returns featured games split into on-sale (with discounts and prices)
    and regular featured titles.
    """
    try:
        result = _get_client().get_featured_games()
        return json.dumps(result, indent=2)
    except (SteamError, ValueError) as e:
        return f"Error: {e}"
