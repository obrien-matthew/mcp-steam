import httpx
import pytest

FAKE_STEAM_ID = "76561198015781444"
FAKE_API_KEY = "FAKEKEYFORTESTING"


@pytest.fixture(autouse=True)
def _reset_auth_singletons(monkeypatch):
    """Prevent SteamClient from hitting real Steam API during init."""
    monkeypatch.setenv("STEAM_API_KEY", FAKE_API_KEY)
    monkeypatch.setenv("STEAM_ID", FAKE_STEAM_ID)

    import steam_mcp.auth as auth_mod

    monkeypatch.setattr(auth_mod, "_client", httpx.Client())
    monkeypatch.setattr(auth_mod, "_steam_id", FAKE_STEAM_ID)

    # Reset the server-level client singleton so each test gets a fresh one
    import steam_mcp.server as server_mod

    monkeypatch.setattr(server_mod, "_client", None)
