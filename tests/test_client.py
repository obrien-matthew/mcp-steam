import httpx
import pytest
import respx

from steam_mcp.client import SteamClient, SteamError

from .conftest import FAKE_API_KEY, FAKE_STEAM_ID

API_BASE = "https://api.steampowered.com"
STORE_BASE = "https://store.steampowered.com"


@pytest.fixture
def client():
    return SteamClient()


class TestResolveUser:
    @respx.mock
    def test_none_returns_configured_id(self, client):
        assert client._resolve_user(None) == FAKE_STEAM_ID

    @respx.mock
    def test_numeric_id_passes_through(self, client):
        sid = "76561198012345678"
        assert client._resolve_user(sid) == sid

    @respx.mock
    def test_vanity_name_resolves(self, client):
        respx.get(f"{API_BASE}/ISteamUser/ResolveVanityURL/v1/").mock(
            return_value=httpx.Response(
                200,
                json={
                    "response": {"success": 1, "steamid": "76561197960287930"},
                },
            )
        )
        assert client._resolve_user("gabelogannewell") == "76561197960287930"

    @respx.mock
    def test_vanity_name_not_found(self, client):
        respx.get(f"{API_BASE}/ISteamUser/ResolveVanityURL/v1/").mock(
            return_value=httpx.Response(
                200,
                json={
                    "response": {"success": 42, "message": "No match"},
                },
            )
        )
        with pytest.raises(SteamError, match="Could not resolve"):
            client._resolve_user("nonexistentuser999999")


class TestResolveVanityUrl:
    @respx.mock
    def test_success(self, client):
        respx.get(f"{API_BASE}/ISteamUser/ResolveVanityURL/v1/").mock(
            return_value=httpx.Response(
                200,
                json={
                    "response": {"success": 1, "steamid": "76561197960287930"},
                },
            )
        )
        result = client.resolve_vanity_url("gabelogannewell")
        assert result == "76561197960287930"

    @respx.mock
    def test_passes_api_key(self, client):
        route = respx.get(f"{API_BASE}/ISteamUser/ResolveVanityURL/v1/").mock(
            return_value=httpx.Response(
                200,
                json={
                    "response": {"success": 1, "steamid": "123"},
                },
            )
        )
        client.resolve_vanity_url("test")
        assert route.calls[0].request.url.params["key"] == FAKE_API_KEY


class TestGetOwnedGames:
    @respx.mock
    def test_sorts_by_playtime(self, client):
        respx.get(f"{API_BASE}/IPlayerService/GetOwnedGames/v1/").mock(
            return_value=httpx.Response(
                200,
                json={
                    "response": {
                        "games": [
                            {"name": "Low", "appid": 1, "playtime_forever": 10},
                            {"name": "High", "appid": 2, "playtime_forever": 100},
                        ]
                    }
                },
            )
        )
        result = client.get_owned_games(sort_by="playtime", limit=10)
        assert result[0]["name"] == "High"
        assert result[1]["name"] == "Low"

    @respx.mock
    def test_sorts_by_name(self, client):
        respx.get(f"{API_BASE}/IPlayerService/GetOwnedGames/v1/").mock(
            return_value=httpx.Response(
                200,
                json={
                    "response": {
                        "games": [
                            {"name": "Zelda", "appid": 1, "playtime_forever": 0},
                            {"name": "Aardvark", "appid": 2, "playtime_forever": 0},
                        ]
                    }
                },
            )
        )
        result = client.get_owned_games(sort_by="name", limit=10)
        assert result[0]["name"] == "Aardvark"

    @respx.mock
    def test_respects_limit(self, client):
        games = [
            {"name": f"Game{i}", "appid": i, "playtime_forever": i} for i in range(20)
        ]
        respx.get(f"{API_BASE}/IPlayerService/GetOwnedGames/v1/").mock(
            return_value=httpx.Response(200, json={"response": {"games": games}})
        )
        result = client.get_owned_games(limit=5)
        assert len(result) == 5


class TestGetGameDetails:
    @respx.mock
    def test_success(self, client):
        respx.get(f"{STORE_BASE}/api/appdetails").mock(
            return_value=httpx.Response(
                200,
                json={
                    "730": {
                        "success": True,
                        "data": {
                            "name": "CS2",
                            "steam_appid": 730,
                            "type": "game",
                            "short_description": "Shooter",
                        },
                    }
                },
            )
        )
        result = client.get_game_details("730")
        assert result["name"] == "CS2"

    @respx.mock
    def test_not_found(self, client):
        respx.get(f"{STORE_BASE}/api/appdetails").mock(
            return_value=httpx.Response(200, json={"99999": {"success": False}})
        )
        with pytest.raises(SteamError, match="not found"):
            client.get_game_details("99999")


class TestGetAchievements:
    @respx.mock
    def test_merges_global_percentages(self, client):
        respx.get(f"{API_BASE}/ISteamUserStats/GetPlayerAchievements/v1/").mock(
            return_value=httpx.Response(
                200,
                json={
                    "playerstats": {
                        "gameName": "Test",
                        "achievements": [
                            {
                                "apiname": "ACH_1",
                                "achieved": 1,
                                "unlocktime": 1700000000,
                            },
                            {"apiname": "ACH_2", "achieved": 0, "unlocktime": 0},
                        ],
                    }
                },
            )
        )
        respx.get(
            f"{API_BASE}/ISteamUserStats/GetGlobalAchievementPercentagesForApp/v2/"
        ).mock(
            return_value=httpx.Response(
                200,
                json={
                    "achievementpercentages": {
                        "achievements": [
                            {"name": "ACH_1", "percent": "85.5"},
                            {"name": "ACH_2", "percent": "12.3"},
                        ]
                    }
                },
            )
        )
        result = client.get_achievements("730")
        assert result["unlocked"] == 1
        assert result["total"] == 2
        assert result["achievements"][0]["global_percent"] == 85.5

    @respx.mock
    def test_works_without_global_percentages(self, client):
        respx.get(f"{API_BASE}/ISteamUserStats/GetPlayerAchievements/v1/").mock(
            return_value=httpx.Response(
                200,
                json={
                    "playerstats": {
                        "gameName": "Test",
                        "achievements": [
                            {"apiname": "ACH_1", "achieved": 1, "unlocktime": 0},
                        ],
                    }
                },
            )
        )
        # Global percentages endpoint fails
        respx.get(
            f"{API_BASE}/ISteamUserStats/GetGlobalAchievementPercentagesForApp/v2/"
        ).mock(return_value=httpx.Response(500))
        result = client.get_achievements("730")
        assert result["total"] == 1
        assert "global_percent" not in result["achievements"][0]


class TestGetPlayerSummary:
    @respx.mock
    def test_own_profile(self, client):
        respx.get(f"{API_BASE}/ISteamUser/GetPlayerSummaries/v2/").mock(
            return_value=httpx.Response(
                200,
                json={
                    "response": {
                        "players": [
                            {
                                "personaname": "Me",
                                "steamid": FAKE_STEAM_ID,
                                "personastate": 1,
                                "profileurl": "https://example.com",
                            }
                        ]
                    }
                },
            )
        )
        result = client.get_player_summary()
        assert result["name"] == "Me"

    @respx.mock
    def test_other_player_by_vanity(self, client):
        respx.get(f"{API_BASE}/ISteamUser/ResolveVanityURL/v1/").mock(
            return_value=httpx.Response(
                200,
                json={
                    "response": {"success": 1, "steamid": "76561197960287930"},
                },
            )
        )
        respx.get(f"{API_BASE}/ISteamUser/GetPlayerSummaries/v2/").mock(
            return_value=httpx.Response(
                200,
                json={
                    "response": {
                        "players": [
                            {
                                "personaname": "Gabe",
                                "steamid": "76561197960287930",
                                "personastate": 0,
                                "profileurl": "",
                            }
                        ]
                    }
                },
            )
        )
        result = client.get_player_summary("gabelogannewell")
        assert result["name"] == "Gabe"


class TestGetAppReviews:
    @respx.mock
    def test_success(self, client):
        respx.get(f"{STORE_BASE}/appreviews/730").mock(
            return_value=httpx.Response(
                200,
                json={
                    "success": 1,
                    "query_summary": {
                        "total_reviews": 1000,
                        "total_positive": 900,
                        "total_negative": 100,
                        "review_score_desc": "Very Positive",
                    },
                    "reviews": [
                        {
                            "voted_up": True,
                            "review": "Great game!",
                            "author": {"playtime_at_review": 60},
                            "votes_up": 5,
                            "votes_funny": 0,
                            "timestamp_created": 1700000000,
                        },
                    ],
                },
            )
        )
        result = client.get_app_reviews("730")
        assert result["total_reviews"] == 1000
        assert result["review_score_desc"] == "Very Positive"
        assert len(result["reviews"]) == 1
        assert result["reviews"][0]["recommended"] is True

    @respx.mock
    def test_invalid_review_type_defaults(self, client):
        respx.get(f"{STORE_BASE}/appreviews/730").mock(
            return_value=httpx.Response(
                200,
                json={
                    "success": 1,
                    "query_summary": {},
                    "reviews": [],
                },
            )
        )
        # Should not raise -- invalid type defaults to "all"
        result = client.get_app_reviews("730", review_type="invalid")
        assert isinstance(result, dict)


class TestGetFeaturedGames:
    @respx.mock
    def test_deduplicates(self, client):
        game = {"name": "Duped", "id": 100, "discounted": False, "final_price": 999}
        respx.get(f"{STORE_BASE}/api/featured").mock(
            return_value=httpx.Response(
                200,
                json={
                    "featured_win": [game],
                    "featured_mac": [game],
                    "featured_linux": [game],
                },
            )
        )
        result = client.get_featured_games()
        assert result["total"] == 1

    @respx.mock
    def test_splits_on_sale_and_regular(self, client):
        respx.get(f"{STORE_BASE}/api/featured").mock(
            return_value=httpx.Response(
                200,
                json={
                    "featured_win": [
                        {
                            "name": "Sale",
                            "id": 1,
                            "discounted": True,
                            "discount_percent": 50,
                            "final_price": 499,
                            "original_price": 999,
                        },
                        {
                            "name": "Full",
                            "id": 2,
                            "discounted": False,
                            "final_price": 1999,
                        },
                    ],
                    "featured_mac": [],
                    "featured_linux": [],
                },
            )
        )
        result = client.get_featured_games()
        assert len(result["on_sale"]) == 1
        assert len(result["regular"]) == 1
        assert result["on_sale"][0]["name"] == "Sale"


class TestGetCurrentPlayers:
    @respx.mock
    def test_success(self, client):
        respx.get(f"{API_BASE}/ISteamUserStats/GetNumberOfCurrentPlayers/v1/").mock(
            return_value=httpx.Response(200, json={"response": {"player_count": 50000}})
        )
        result = client.get_current_players("730")
        assert result["player_count"] == 50000
        assert result["app_id"] == 730


class TestGetPackageDetails:
    @respx.mock
    def test_success(self, client):
        respx.get(f"{STORE_BASE}/api/packagedetails").mock(
            return_value=httpx.Response(
                200,
                json={
                    "123": {
                        "success": True,
                        "data": {
                            "name": "Bundle",
                            "apps": [{"id": 1, "name": "Game"}],
                            "price": {"final": 999, "discount_percent": 0},
                        },
                    }
                },
            )
        )
        result = client.get_package_details("123")
        assert result["name"] == "Bundle"

    @respx.mock
    def test_not_found(self, client):
        respx.get(f"{STORE_BASE}/api/packagedetails").mock(
            return_value=httpx.Response(200, json={"999": {"success": False}})
        )
        with pytest.raises(SteamError, match="not found"):
            client.get_package_details("999")
