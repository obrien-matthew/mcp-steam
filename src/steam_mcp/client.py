"""Thin wrapper over the Steam Web API with validation and clean error handling."""

import sys
from typing import Any, NoReturn

import httpx

from .auth import get_api_key, get_http_client, get_steam_id
from .formatting import (
    format_achievement,
    format_featured_game,
    format_friend,
    format_game_details,
    format_news_item,
    format_owned_game,
    format_player_summary,
    format_wishlist_item,
)
from .validation import validate_app_id, validate_limit

STEAM_API_BASE = "https://api.steampowered.com"
STORE_API_BASE = "https://store.steampowered.com"


class SteamError(Exception):
    """User-facing Steam API error."""

    def __init__(self, message: str, status_code: int | None = None):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class SteamClient:
    """Validated, formatted interface to the Steam API."""

    def __init__(self) -> None:
        self._http = get_http_client()
        self._api_key = get_api_key()
        self._steam_id = get_steam_id()

    def _handle_error(self, e: Exception, action: str) -> NoReturn:
        msg = f"Steam API error while {action}"
        status_code: int | None = None
        if isinstance(e, httpx.HTTPStatusError):
            status_code = e.response.status_code
            if status_code == 403:
                msg = f"Access denied while {action} (check API key permissions)"
            elif status_code == 404:
                msg = f"Not found while {action}"
            elif status_code == 429:
                msg = f"Rate limited while {action}. Please try again shortly."
            elif status_code == 500:
                msg = f"Steam server error while {action}. Try again later."
        print(f"{msg}: {e}", file=sys.stderr)
        raise SteamError(msg, status_code) from e

    def _api_request(self, endpoint: str, params: dict[str, Any] | None = None) -> dict:
        """Make a request to the Steam Web API (api.steampowered.com)."""
        url = f"{STEAM_API_BASE}/{endpoint}"
        request_params: dict[str, Any] = {"key": self._api_key}
        if params:
            request_params.update(params)
        resp = self._http.get(url, params=request_params)
        resp.raise_for_status()
        return resp.json()

    def _store_request(self, path: str, params: dict[str, Any] | None = None) -> dict:
        """Make a request to the Steam Store API (store.steampowered.com)."""
        url = f"{STORE_API_BASE}/{path}"
        resp = self._http.get(url, params=params or {})
        resp.raise_for_status()
        return resp.json()

    # -- Library --

    def get_owned_games(self, sort_by: str = "playtime", limit: int = 50) -> list[dict]:
        limit = validate_limit(limit, max_val=100)
        try:
            data = self._api_request(
                "IPlayerService/GetOwnedGames/v1/",
                {
                    "steamid": self._steam_id,
                    "include_appinfo": 1,
                    "include_played_free_games": 1,
                },
            )
            games = data.get("response", {}).get("games", [])
            if sort_by == "playtime":
                games.sort(key=lambda g: g.get("playtime_forever", 0), reverse=True)
            elif sort_by == "recent":
                games.sort(key=lambda g: g.get("rtime_last_played", 0), reverse=True)
            elif sort_by == "name":
                games.sort(key=lambda g: g.get("name", "").lower())
            return [format_owned_game(g) for g in games[:limit]]
        except httpx.HTTPStatusError as e:
            self._handle_error(e, "fetching owned games")

    def get_recently_played(self, limit: int = 10) -> list[dict]:
        limit = validate_limit(limit)
        try:
            data = self._api_request(
                "IPlayerService/GetRecentlyPlayedGames/v1/",
                {"steamid": self._steam_id, "count": limit},
            )
            games = data.get("response", {}).get("games", [])
            return [format_owned_game(g) for g in games]
        except httpx.HTTPStatusError as e:
            self._handle_error(e, "fetching recently played games")

    # -- Game Info --

    def get_game_details(self, app_id: str) -> dict:
        app_id_int = validate_app_id(app_id)
        try:
            data = self._store_request(
                "api/appdetails",
                {"appids": str(app_id_int)},
            )
            app_data = data.get(str(app_id_int), {})
            if not app_data.get("success"):
                raise SteamError(f"App {app_id_int} not found on Steam Store")
            return format_game_details(app_data.get("data", {}))
        except httpx.HTTPStatusError as e:
            self._handle_error(e, "fetching game details")

    def search_games(self, query: str, limit: int = 10) -> list[dict]:
        limit = validate_limit(limit, max_val=25)
        try:
            data = self._store_request(
                "api/storesearch",
                {"term": query, "l": "english", "cc": "us"},
            )
            items = data.get("items", [])[:limit]
            results: list[dict] = []
            for item in items:
                results.append(
                    {
                        "name": item.get("name", ""),
                        "appid": item.get("id"),
                        "price": item.get("price", {}).get("final", 0),
                        "platforms": {
                            k: v for k, v in item.get("platforms", {}).items() if v
                        },
                    }
                )
            return results
        except httpx.HTTPStatusError as e:
            self._handle_error(e, "searching games")

    # -- Achievements & Stats --

    def get_achievements(self, app_id: str) -> dict:
        app_id_int = validate_app_id(app_id)
        try:
            data = self._api_request(
                "ISteamUserStats/GetPlayerAchievements/v1/",
                {"steamid": self._steam_id, "appid": app_id_int},
            )
            stats = data.get("playerstats", {})
            achievements = stats.get("achievements", [])

            # Try to get global percentages for context
            global_pcts = self._get_global_percentages(app_id_int)

            formatted = [format_achievement(a, global_pcts) for a in achievements]
            unlocked = sum(1 for a in formatted if a.get("achieved"))
            return {
                "game": stats.get("gameName", ""),
                "unlocked": unlocked,
                "total": len(formatted),
                "achievements": formatted,
            }
        except httpx.HTTPStatusError as e:
            self._handle_error(e, "fetching achievements")

    def _get_global_percentages(self, app_id: int) -> dict[str, float]:
        """Fetch global achievement percentages for enrichment."""
        try:
            data = self._api_request(
                "ISteamUserStats/GetGlobalAchievementPercentagesForApp/v2/",
                {"gameid": app_id},
            )
            achievements = data.get("achievementpercentages", {}).get(
                "achievements", []
            )
            return {a["name"]: a["percent"] for a in achievements}
        except Exception:
            return {}

    def get_player_stats(self, app_id: str) -> dict:
        app_id_int = validate_app_id(app_id)
        try:
            data = self._api_request(
                "ISteamUserStats/GetUserStatsForGame/v2/",
                {"steamid": self._steam_id, "appid": app_id_int},
            )
            stats = data.get("playerstats", {})
            return {
                "game": stats.get("gameName", ""),
                "stats": {s["name"]: s["value"] for s in stats.get("stats", [])},
            }
        except httpx.HTTPStatusError as e:
            self._handle_error(e, "fetching player stats")

    def get_global_achievement_stats(self, app_id: str) -> list[dict]:
        app_id_int = validate_app_id(app_id)
        try:
            data = self._api_request(
                "ISteamUserStats/GetGlobalAchievementPercentagesForApp/v2/",
                {"gameid": app_id_int},
            )
            achievements = data.get("achievementpercentages", {}).get(
                "achievements", []
            )
            return [
                {
                    "name": a.get("name", ""),
                    "percent": round(a.get("percent", 0.0), 1),
                }
                for a in achievements
            ]
        except httpx.HTTPStatusError as e:
            self._handle_error(e, "fetching global achievement stats")

    # -- Wishlist --

    def get_wishlist(self, limit: int = 50) -> list[dict]:
        limit = validate_limit(limit, max_val=100)
        try:
            data = self._store_request(
                f"wishlist/profiles/{self._steam_id}/wishlistdata",
            )
            items = [
                format_wishlist_item(appid, info)
                for appid, info in data.items()
                if isinstance(info, dict)
            ]
            # Sort by priority (0 = no priority, otherwise lower = higher priority)
            items.sort(
                key=lambda x: (
                    x.get("priority", 0) == 0,
                    x.get("priority", 0),
                )
            )
            return items[:limit]
        except httpx.HTTPStatusError as e:
            self._handle_error(e, "fetching wishlist")

    # -- News --

    def get_game_news(self, app_id: str, count: int = 5) -> list[dict]:
        app_id_int = validate_app_id(app_id)
        count = validate_limit(count, max_val=20)
        try:
            data = self._api_request(
                "ISteamNews/GetNewsForApp/v2/",
                {"appid": app_id_int, "count": count, "maxlength": 500},
            )
            items = data.get("appnews", {}).get("newsitems", [])
            return [format_news_item(item) for item in items]
        except httpx.HTTPStatusError as e:
            self._handle_error(e, "fetching game news")

    # -- Profile --

    def get_player_summary(self) -> dict:
        try:
            data = self._api_request(
                "ISteamUser/GetPlayerSummaries/v2/",
                {"steamids": self._steam_id},
            )
            players = data.get("response", {}).get("players", [])
            if not players:
                raise SteamError("Player profile not found")
            return format_player_summary(players[0])
        except httpx.HTTPStatusError as e:
            self._handle_error(e, "fetching player summary")

    def get_friend_list(self) -> list[dict]:
        try:
            data = self._api_request(
                "ISteamUser/GetFriendList/v1/",
                {"steamid": self._steam_id, "relationship": "friend"},
            )
            friends = data.get("friendslist", {}).get("friends", [])
            return [format_friend(f) for f in friends]
        except httpx.HTTPStatusError as e:
            self._handle_error(e, "fetching friend list")

    # -- Featured --

    def get_featured_games(self) -> dict:
        try:
            data = self._store_request("api/featured")
            featured_win = data.get("featured_win", [])
            featured_mac = data.get("featured_mac", [])
            featured_linux = data.get("featured_linux", [])

            # Combine and deduplicate by appid
            seen: set[int] = set()
            all_featured: list[dict] = []
            for game in featured_win + featured_mac + featured_linux:
                appid = game.get("id")
                if appid and appid not in seen:
                    seen.add(appid)
                    all_featured.append(format_featured_game(game))

            # Separate into on-sale and regular
            on_sale = [g for g in all_featured if g.get("discounted")]
            regular = [g for g in all_featured if not g.get("discounted")]

            return {
                "on_sale": on_sale,
                "regular": regular,
                "total": len(all_featured),
            }
        except httpx.HTTPStatusError as e:
            self._handle_error(e, "fetching featured games")
