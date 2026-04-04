"""Response formatters that produce clean, LLM-friendly dicts.

Only includes fields useful for an LLM -- no images, screenshots, or raw HTML.
"""

import re
from datetime import UTC, datetime
from typing import Any

from .validation import format_playtime


def format_owned_game(game: dict) -> dict:
    """Format a game from the owned games list."""
    result: dict[str, Any] = {
        "name": game.get("name", "Unknown"),
        "appid": game.get("appid"),
        "playtime_total": format_playtime(game.get("playtime_forever", 0)),
    }
    playtime_2weeks = game.get("playtime_2weeks")
    if playtime_2weeks:
        result["playtime_2weeks"] = format_playtime(playtime_2weeks)
    last_played = game.get("rtime_last_played")
    if last_played and last_played > 0:
        result["last_played"] = datetime.fromtimestamp(last_played, tz=UTC).isoformat()
    return result


def format_game_details(data: dict) -> dict:
    """Format store app details into an LLM-friendly dict."""
    result: dict[str, Any] = {
        "name": data.get("name", "Unknown"),
        "appid": data.get("steam_appid"),
        "type": data.get("type"),
        "is_free": data.get("is_free", False),
        "description": data.get("short_description", ""),
    }

    # Price
    price_overview = data.get("price_overview")
    if price_overview:
        result["price"] = price_overview.get("final_formatted", "")
        discount = price_overview.get("discount_percent", 0)
        if discount > 0:
            result["discount_percent"] = discount
    elif data.get("is_free"):
        result["price"] = "Free"

    # Reviews
    if data.get("metacritic"):
        result["metacritic_score"] = data["metacritic"].get("score")

    # Genres
    genres = data.get("genres", [])
    if genres:
        result["genres"] = [g.get("description", "") for g in genres]

    # Release date
    release = data.get("release_date", {})
    if release:
        result["release_date"] = release.get("date", "")
        result["coming_soon"] = release.get("coming_soon", False)

    # Platforms
    platforms = data.get("platforms", {})
    supported = [p for p, v in platforms.items() if v]
    if supported:
        result["platforms"] = supported

    return result


def format_achievement(ach: dict, global_percentages: dict | None = None) -> dict:
    """Format a player achievement."""
    result: dict[str, Any] = {
        "name": ach.get("apiname", ach.get("name", "")),
        "achieved": bool(ach.get("achieved", 0)),
    }
    display_name = ach.get("name")
    if display_name and display_name != result["name"]:
        result["display_name"] = display_name
    description = ach.get("description")
    if description:
        result["description"] = description
    unlock_time = ach.get("unlocktime", 0)
    if unlock_time > 0:
        result["unlocked_at"] = datetime.fromtimestamp(unlock_time, tz=UTC).isoformat()
    if global_percentages and result["name"] in global_percentages:
        result["global_percent"] = round(float(global_percentages[result["name"]]), 1)
    return result


def format_player_summary(player: dict) -> dict:
    """Format a Steam player summary."""
    status_map = {
        0: "offline",
        1: "online",
        2: "busy",
        3: "away",
        4: "snooze",
        5: "looking to trade",
        6: "looking to play",
    }
    result: dict[str, Any] = {
        "name": player.get("personaname", ""),
        "steamid": player.get("steamid", ""),
        "status": status_map.get(player.get("personastate", 0), "unknown"),
        "profile_url": player.get("profileurl", ""),
    }
    last_logoff = player.get("lastlogoff")
    if last_logoff:
        result["last_logoff"] = datetime.fromtimestamp(last_logoff, tz=UTC).isoformat()
    game_name = player.get("gameextrainfo")
    if game_name:
        result["currently_playing"] = game_name
    return result


def format_news_item(item: dict) -> dict:
    """Format a Steam news item."""
    contents = item.get("contents", "")
    # Truncate long content for LLM consumption
    if len(contents) > 500:
        contents = contents[:500] + "..."
    result: dict[str, Any] = {
        "title": item.get("title", ""),
        "author": item.get("author", ""),
        "contents": contents,
        "url": item.get("url", ""),
    }
    date = item.get("date")
    if date:
        result["date"] = datetime.fromtimestamp(date, tz=UTC).isoformat()
    return result


def format_wishlist_item(appid: str, item: dict) -> dict:
    """Format a wishlist item."""
    result: dict[str, Any] = {
        "name": item.get("name", "Unknown"),
        "appid": int(appid),
        "priority": item.get("priority", 0),
    }
    subs = item.get("subs", [])
    if subs:
        for sub in subs:
            if "price" in sub:
                # Price is in cents
                price_cents = sub["price"]
                result["price"] = f"${price_cents / 100:.2f}"
                discount = sub.get("discount_pct", 0)
                if discount > 0:
                    result["discount_percent"] = discount
                break
    added = item.get("added")
    if added:
        result["added_at"] = datetime.fromtimestamp(added, tz=UTC).isoformat()
    return result


def format_friend(friend: dict) -> dict:
    """Format a friend entry."""
    result: dict[str, Any] = {
        "steamid": friend.get("steamid", ""),
        "relationship": friend.get("relationship", ""),
    }
    friends_since = friend.get("friend_since", 0)
    if friends_since > 0:
        result["friends_since"] = datetime.fromtimestamp(
            friends_since, tz=UTC
        ).isoformat()
    return result


def format_player_bans(player: dict) -> dict:
    """Format a player ban record."""
    return {
        "steamid": player.get("SteamId", ""),
        "community_banned": player.get("CommunityBanned", False),
        "vac_banned": player.get("VACBanned", False),
        "vac_bans": player.get("NumberOfVACBans", 0),
        "days_since_last_ban": player.get("DaysSinceLastBan", 0),
        "game_bans": player.get("NumberOfGameBans", 0),
        "economy_ban": player.get("EconomyBan", "none"),
    }


def format_game_schema(data: dict) -> dict:
    """Format a game stats schema into achievement/stat definitions."""
    available = data.get("availableGameStats", {})
    achievements = []
    for ach in available.get("achievements", []):
        entry: dict[str, Any] = {
            "name": ach.get("name", ""),
            "display_name": ach.get("displayName", ""),
        }
        desc = ach.get("description")
        if desc:
            entry["description"] = desc
        hidden = ach.get("hidden", 0)
        if hidden:
            entry["hidden"] = True
        achievements.append(entry)

    stats = []
    for stat in available.get("stats", []):
        stats.append(
            {
                "name": stat.get("name", ""),
                "display_name": stat.get("displayName", ""),
            }
        )

    result: dict[str, Any] = {
        "game": data.get("gameName", ""),
    }
    if achievements:
        result["achievements"] = achievements
        result["achievement_count"] = len(achievements)
    if stats:
        result["stats"] = stats
        result["stat_count"] = len(stats)
    return result


def _strip_html(text: str) -> str:
    """Remove HTML tags and decode common entities."""
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    text = text.replace("&quot;", '"').replace("&#39;", "'")
    return text.strip()


def format_review(review: dict) -> dict:
    """Format a Steam user review."""
    text = _strip_html(review.get("review", ""))
    if len(text) > 500:
        text = text[:500] + "..."
    result: dict[str, Any] = {
        "recommended": review.get("voted_up", False),
        "text": text,
        "playtime_at_review": format_playtime(
            review.get("author", {}).get("playtime_at_review", 0)
        ),
        "votes_up": review.get("votes_up", 0),
        "votes_funny": review.get("votes_funny", 0),
    }
    timestamp = review.get("timestamp_created")
    if timestamp:
        result["date"] = datetime.fromtimestamp(timestamp, tz=UTC).isoformat()
    return result


def format_featured_category(category: dict) -> dict:
    """Format a featured store category (Top Sellers, New Releases, etc.)."""
    items = []
    for item in category.get("items", []):
        entry: dict[str, Any] = {
            "name": item.get("name", "Unknown"),
            "appid": item.get("id"),
        }
        if item.get("discounted"):
            entry["discount_percent"] = item.get("discount_percent", 0)
            final = item.get("final_price", 0)
            entry["price"] = f"${final / 100:.2f}"
            original = item.get("original_price", 0)
            if original:
                entry["original_price"] = f"${original / 100:.2f}"
        else:
            final = item.get("final_price", 0)
            if final > 0:
                entry["price"] = f"${final / 100:.2f}"
            elif item.get("free"):
                entry["price"] = "Free"
        items.append(entry)
    return {
        "name": category.get("name", ""),
        "count": len(items),
        "items": items,
    }


def format_package_details(data: dict) -> dict:
    """Format a Steam package/bundle."""
    result: dict[str, Any] = {
        "name": data.get("name", "Unknown"),
        "page_content": data.get("page_content", ""),
    }
    price = data.get("price", {})
    if price:
        final = price.get("final", 0)
        result["price"] = f"${final / 100:.2f}"
        discount = price.get("discount_percent", 0)
        if discount > 0:
            result["discount_percent"] = discount
            initial = price.get("initial", 0)
            result["original_price"] = f"${initial / 100:.2f}"
    apps = data.get("apps", [])
    if apps:
        result["apps"] = [
            {"appid": a.get("id"), "name": a.get("name", "")} for a in apps
        ]
        result["app_count"] = len(apps)
    platforms = data.get("platforms", {})
    supported = [p for p, v in platforms.items() if v]
    if supported:
        result["platforms"] = supported
    release = data.get("release_date", {})
    if release:
        result["release_date"] = release.get("date", "")
    return result


def format_featured_game(game: dict) -> dict:
    """Format a featured/sale game."""
    result: dict[str, Any] = {
        "name": game.get("name", "Unknown"),
        "appid": game.get("id"),
        "discounted": game.get("discounted", False),
    }
    if game.get("discounted"):
        result["discount_percent"] = game.get("discount_percent", 0)
        final_price = game.get("final_price", 0)
        result["price"] = f"${final_price / 100:.2f}"
        original_price = game.get("original_price", 0)
        if original_price:
            result["original_price"] = f"${original_price / 100:.2f}"
    else:
        final_price = game.get("final_price", 0)
        if final_price > 0:
            result["price"] = f"${final_price / 100:.2f}"
        elif game.get("free"):
            result["price"] = "Free"
    return result
