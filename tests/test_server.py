"""Smoke tests for MCP tool wrappers -- verify return shapes and error handling."""

from importlib.metadata import version

import httpx
import pytest
import respx

from steam_mcp.client import SteamError
from steam_mcp.server import (
    get_achievements,
    get_app_reviews,
    get_current_players,
    get_featured_categories,
    get_featured_games,
    get_friend_list,
    get_game_details,
    get_game_news,
    get_game_schema,
    get_global_achievement_stats,
    get_owned_games,
    get_package_details,
    get_player_bans,
    get_player_stats,
    get_player_summary,
    get_recently_played,
    get_server_version,
    get_steam_level,
    get_wishlist,
    resolve_vanity_url,
    search_games,
)


class TestGetServerVersion:
    def test_returns_installed_version(self):
        assert get_server_version() == version("mcp-steam")


API_BASE = "https://api.steampowered.com"
STORE_BASE = "https://store.steampowered.com"


def _mock_api(endpoint, response_json, status=200):
    return respx.get(f"{API_BASE}/{endpoint}").mock(
        return_value=httpx.Response(status, json=response_json)
    )


def _mock_store(path, response_json, status=200):
    return respx.get(f"{STORE_BASE}/{path}").mock(
        return_value=httpx.Response(status, json=response_json)
    )


class TestToolsReturnStructuredData:
    @respx.mock
    def test_resolve_vanity_url(self):
        _mock_api(
            "ISteamUser/ResolveVanityURL/v1/",
            {
                "response": {"success": 1, "steamid": "123"},
            },
        )
        result = resolve_vanity_url("test")
        assert result == "123"

    @respx.mock
    def test_get_owned_games(self):
        _mock_api(
            "IPlayerService/GetOwnedGames/v1/",
            {
                "response": {
                    "games": [{"name": "G", "appid": 1, "playtime_forever": 0}]
                },
            },
        )
        result = get_owned_games()
        assert isinstance(result, list)

    @respx.mock
    def test_get_recently_played(self):
        _mock_api(
            "IPlayerService/GetRecentlyPlayedGames/v1/",
            {
                "response": {"games": []},
            },
        )
        result = get_recently_played()
        assert isinstance(result, list)

    @respx.mock
    def test_get_game_details(self):
        _mock_store(
            "api/appdetails",
            {
                "730": {"success": True, "data": {"name": "CS2", "steam_appid": 730}},
            },
        )
        result = get_game_details("730")
        assert result["name"] == "CS2"

    @respx.mock
    def test_search_games(self):
        _mock_store("api/storesearch", {"items": []})
        result = search_games("test")
        assert isinstance(result, list)

    @respx.mock
    def test_get_achievements(self):
        _mock_api(
            "ISteamUserStats/GetPlayerAchievements/v1/",
            {
                "playerstats": {"gameName": "T", "achievements": []},
            },
        )
        _mock_api(
            "ISteamUserStats/GetGlobalAchievementPercentagesForApp/v2/",
            {
                "achievementpercentages": {"achievements": []},
            },
        )
        result = get_achievements("730")
        assert "total" in result

    @respx.mock
    def test_get_player_stats(self):
        _mock_api(
            "ISteamUserStats/GetUserStatsForGame/v2/",
            {
                "playerstats": {"gameName": "T", "stats": []},
            },
        )
        result = get_player_stats("730")
        assert "game" in result

    @respx.mock
    def test_get_global_achievement_stats(self):
        _mock_api(
            "ISteamUserStats/GetGlobalAchievementPercentagesForApp/v2/",
            {
                "achievementpercentages": {"achievements": []},
            },
        )
        result = get_global_achievement_stats("730")
        assert isinstance(result, list)

    @respx.mock
    def test_get_wishlist(self):
        _mock_store("wishlist/profiles/76561198015781444/wishlistdata", {})
        result = get_wishlist()
        assert isinstance(result, list)

    @respx.mock
    def test_get_game_news(self):
        _mock_api(
            "ISteamNews/GetNewsForApp/v2/",
            {
                "appnews": {"newsitems": []},
            },
        )
        result = get_game_news("730")
        assert isinstance(result, list)

    @respx.mock
    def test_get_player_summary(self):
        _mock_api(
            "ISteamUser/GetPlayerSummaries/v2/",
            {
                "response": {
                    "players": [
                        {
                            "personaname": "Me",
                            "steamid": "123",
                            "personastate": 1,
                            "profileurl": "",
                        }
                    ]
                },
            },
        )
        result = get_player_summary()
        assert result["name"] == "Me"

    @respx.mock
    def test_get_friend_list(self):
        _mock_api(
            "ISteamUser/GetFriendList/v1/",
            {
                "friendslist": {"friends": []},
            },
        )
        result = get_friend_list()
        assert isinstance(result, list)

    @respx.mock
    def test_get_player_bans(self):
        _mock_api(
            "ISteamUser/GetPlayerBans/v1/",
            {
                "players": [
                    {
                        "SteamId": "123",
                        "CommunityBanned": False,
                        "VACBanned": False,
                        "NumberOfVACBans": 0,
                        "DaysSinceLastBan": 0,
                        "NumberOfGameBans": 0,
                        "EconomyBan": "none",
                    }
                ],
            },
        )
        result = get_player_bans()
        assert "vac_banned" in result

    @respx.mock
    def test_get_steam_level(self):
        _mock_api(
            "IPlayerService/GetSteamLevel/v1/",
            {
                "response": {"player_level": 42},
            },
        )
        result = get_steam_level()
        assert result["level"] == 42

    @respx.mock
    def test_get_current_players(self):
        _mock_api(
            "ISteamUserStats/GetNumberOfCurrentPlayers/v1/",
            {
                "response": {"player_count": 1000},
            },
        )
        result = get_current_players("730")
        assert result["player_count"] == 1000

    @respx.mock
    def test_get_game_schema(self):
        _mock_api(
            "ISteamUserStats/GetSchemaForGame/v2/",
            {
                "game": {
                    "gameName": "T",
                    "availableGameStats": {"achievements": [], "stats": []},
                },
            },
        )
        result = get_game_schema("730")
        assert result["game"] == "T"

    @respx.mock
    def test_get_app_reviews(self):
        _mock_store(
            "appreviews/730",
            {
                "success": 1,
                "query_summary": {"total_reviews": 0},
                "reviews": [],
            },
        )
        result = get_app_reviews("730")
        assert "total_reviews" in result

    @respx.mock
    def test_get_featured_categories(self):
        _mock_store(
            "api/featuredcategories",
            {
                "specials": {"name": "Specials", "items": []},
                "status": 1,
            },
        )
        result = get_featured_categories()
        assert "specials" in result

    @respx.mock
    def test_get_package_details(self):
        _mock_store(
            "api/packagedetails",
            {
                "123": {"success": True, "data": {"name": "Pack"}},
            },
        )
        result = get_package_details("123")
        assert result["name"] == "Pack"

    @respx.mock
    def test_get_featured_games(self):
        _mock_store(
            "api/featured",
            {
                "featured_win": [],
                "featured_mac": [],
                "featured_linux": [],
            },
        )
        result = get_featured_games()
        assert "total" in result


class TestToolsPropagateErrors:
    @respx.mock
    def test_steam_error_propagates(self):
        _mock_api("IPlayerService/GetOwnedGames/v1/", {}, status=500)
        with pytest.raises(SteamError):
            get_owned_games()

    def test_validation_error_propagates(self):
        with pytest.raises((ValueError, SteamError)):
            get_game_details("not-a-number")
