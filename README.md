# mcp-steam

MCP server for Steam, focused on gaming library management, achievements, stats, and store discovery. 12 granular tools designed for use with Claude and other LLM agents.

## Prerequisites

- Python 3.14+
- [uv](https://docs.astral.sh/uv/)
- A [Steam Web API Key](https://steamcommunity.com/dev/apikey)
- Your Steam ID (numeric, up to 17 digits)

## Setup

### 1. Get Your Steam API Key

1. Go to the [Steam Web API Key page](https://steamcommunity.com/dev/apikey)
2. Sign in with your Steam account
3. Register a domain name (any name works for personal use)
4. Note your API key

### 2. Find Your Steam ID

Your Steam ID is the numeric identifier in your profile URL. If your profile URL is `https://steamcommunity.com/profiles/76561198012345678`, your Steam ID is `76561198012345678`.

If you use a custom URL (e.g., `/id/username`), use a [Steam ID finder](https://www.steamidfinder.com/) to look up the numeric ID.

### 3. Install

```bash
cd mcp-steam
uv sync
```

### 4. Configure Environment Variables

Set these before running the server:

```bash
export STEAM_API_KEY="your_api_key"
export STEAM_ID="your_steam_id"
```

### 5. Test the Connection

```bash
uv run mcp-steam
```

The server verifies your API key and Steam ID on startup by fetching your player summary.

## Claude Desktop / Claude Code Configuration

Add to your MCP server config. If installed from PyPI:

```json
{
  "mcpServers": {
    "steam": {
      "command": "uvx",
      "args": ["mcp-steam"],
      "env": {
        "STEAM_API_KEY": "your_api_key",
        "STEAM_ID": "your_steam_id"
      }
    }
  }
}
```

Or if running from a local clone:

```json
{
  "mcpServers": {
    "steam": {
      "command": "uv",
      "args": ["--directory", "/path/to/mcp-steam", "run", "mcp-steam"],
      "env": {
        "STEAM_API_KEY": "your_api_key",
        "STEAM_ID": "your_steam_id"
      }
    }
  }
}
```

## Tools

### Library

| Tool | Parameters | Description |
|------|-----------|-------------|
| `get_owned_games` | `sort_by="playtime"`, `limit=50` | Your game library with playtime. Sort by playtime, recent, or name. |
| `get_recently_played` | `limit=10` | Games played in the last 2 weeks. |

### Game Info

| Tool | Parameters | Description |
|------|-----------|-------------|
| `get_game_details` | `app_id` | Store page info: description, price, genres, metacritic, platforms. |
| `search_games` | `query`, `limit=10` | Search the Steam store. |

### Achievements & Stats

| Tool | Parameters | Description |
|------|-----------|-------------|
| `get_achievements` | `app_id` | Your achievement progress with global rarity percentages. |
| `get_player_stats` | `app_id` | Game-specific stats (kills, deaths, etc.). |
| `get_global_achievement_stats` | `app_id` | Global unlock percentages for all achievements. |

### Wishlist

| Tool | Parameters | Description |
|------|-----------|-------------|
| `get_wishlist` | `limit=50` | Your wishlist sorted by priority, with prices and discounts. |

### News

| Tool | Parameters | Description |
|------|-----------|-------------|
| `get_game_news` | `app_id`, `count=5` | Recent news and updates for a game. |

### Profile

| Tool | Parameters | Description |
|------|-----------|-------------|
| `get_player_summary` | (none) | Your profile: name, status, currently playing. |
| `get_friend_list` | (none) | Your friends list with relationship info. |

### Featured

| Tool | Parameters | Description |
|------|-----------|-------------|
| `get_featured_games` | (none) | Currently featured and on-sale games. |

## Steam Web API Notes

- **API key security:** Your config file contains your Steam API key. Never commit it to version control or share it publicly.
- **Rate limits:** The Steam Web API has undocumented rate limits. If you hit them, the server will return a rate limit error.
- **Profile visibility:** Some tools require your Steam profile to be public (achievements, game stats). Library data works regardless.
- **Game stats availability:** Not all games expose stats through the API. `get_player_stats` will return an error for unsupported games.
- **Wishlist access:** Wishlist data requires your profile's wishlist to be public.

## Development

```bash
uv run mcp-steam              # Run the server
uv run ruff check src/       # Lint
uv run ruff format src/      # Format
uv run pyright src/          # Type check
```

### Pre-commit Hooks

This project uses [lefthook](https://github.com/evilmartians/lefthook) for pre-commit checks. Install with `brew install lefthook` (or see [other install methods](https://github.com/evilmartians/lefthook/blob/master/docs/install.md)), then:

```bash
lefthook install
```
