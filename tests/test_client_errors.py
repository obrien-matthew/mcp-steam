import httpx
import pytest
import respx

from steam_mcp.client import SteamClient, SteamError

API_BASE = "https://api.steampowered.com"
STORE_BASE = "https://store.steampowered.com"


@pytest.fixture
def client():
    return SteamClient()


class TestHandleError:
    @respx.mock
    def test_403_access_denied(self, client):
        respx.get(f"{API_BASE}/ISteamUser/GetFriendList/v1/").mock(
            return_value=httpx.Response(403)
        )
        with pytest.raises(SteamError, match="Access denied") as exc_info:
            client.get_friend_list()
        assert exc_info.value.status_code == 403

    @respx.mock
    def test_404_not_found(self, client):
        respx.get(f"{API_BASE}/ISteamUserStats/GetUserStatsForGame/v2/").mock(
            return_value=httpx.Response(404)
        )
        with pytest.raises(SteamError, match="Not found") as exc_info:
            client.get_player_stats("730")
        assert exc_info.value.status_code == 404

    @respx.mock
    def test_429_rate_limited(self, client):
        respx.get(f"{API_BASE}/IPlayerService/GetOwnedGames/v1/").mock(
            return_value=httpx.Response(429)
        )
        with pytest.raises(SteamError, match="Rate limited") as exc_info:
            client.get_owned_games()
        assert exc_info.value.status_code == 429

    @respx.mock
    def test_500_server_error(self, client):
        respx.get(f"{API_BASE}/ISteamNews/GetNewsForApp/v2/").mock(
            return_value=httpx.Response(500)
        )
        with pytest.raises(SteamError, match="Steam server error") as exc_info:
            client.get_game_news("730")
        assert exc_info.value.status_code == 500

    @respx.mock
    def test_generic_http_error(self, client):
        respx.get(f"{API_BASE}/IPlayerService/GetSteamLevel/v1/").mock(
            return_value=httpx.Response(502)
        )
        with pytest.raises(SteamError, match="Steam API error") as exc_info:
            client.get_steam_level()
        assert exc_info.value.status_code == 502


class TestStoreApiErrors:
    @respx.mock
    def test_store_http_error(self, client):
        respx.get(f"{STORE_BASE}/api/appdetails").mock(return_value=httpx.Response(503))
        with pytest.raises(SteamError, match="Steam API error"):
            client.get_game_details("730")

    @respx.mock
    def test_reviews_not_successful(self, client):
        respx.get(f"{STORE_BASE}/appreviews/730").mock(
            return_value=httpx.Response(
                200,
                json={
                    "success": 0,
                },
            )
        )
        with pytest.raises(SteamError, match="Could not fetch reviews"):
            client.get_app_reviews("730")
