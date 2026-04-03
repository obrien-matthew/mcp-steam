"""Steam API key validation and HTTP client singleton."""

import os
import sys

import httpx

_client: httpx.Client | None = None
_steam_id: str | None = None


def get_steam_id() -> str:
    """Return the configured Steam ID."""
    global _steam_id
    if _steam_id is not None:
        return _steam_id

    steam_id = os.environ.get("STEAM_ID")
    if not steam_id:
        raise RuntimeError(
            "STEAM_ID environment variable is required. "
            "See README.md for setup instructions."
        )
    _steam_id = steam_id
    return _steam_id


def get_http_client() -> httpx.Client:
    """Return a cached HTTP client for Steam API calls.

    Reads STEAM_API_KEY from environment variables and verifies
    the key works by fetching the player summary.

    Raises RuntimeError if required env vars are missing or key is invalid.
    """
    global _client
    if _client is not None:
        return _client

    api_key = os.environ.get("STEAM_API_KEY")
    if not api_key:
        raise RuntimeError(
            "STEAM_API_KEY environment variable is required. "
            "See README.md for setup instructions."
        )

    steam_id = get_steam_id()

    client = httpx.Client(timeout=30.0)

    # Verify API key works by fetching player summary
    try:
        resp = client.get(
            "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/",
            params={"key": api_key, "steamids": steam_id},
        )
        resp.raise_for_status()
        data = resp.json()
        players = data.get("response", {}).get("players", [])
        if not players:
            raise RuntimeError(
                f"No player found for Steam ID '{steam_id}'. "
                "Please check your STEAM_ID."
            )
    except httpx.HTTPStatusError as e:
        client.close()
        print(f"Steam API key verification failed: {e}", file=sys.stderr)
        raise RuntimeError(
            "Failed to verify Steam API key. Please check your credentials."
        ) from e
    except Exception as e:
        client.close()
        print(f"Steam API connection failed: {e}", file=sys.stderr)
        raise RuntimeError(
            "Failed to connect to Steam API. Please check your network."
        ) from e

    _client = client
    return _client


def get_api_key() -> str:
    """Return the Steam API key from environment."""
    api_key = os.environ.get("STEAM_API_KEY")
    if not api_key:
        raise RuntimeError("STEAM_API_KEY environment variable is required.")
    return api_key
