from steam_mcp.formatting import (
    _strip_html,
    format_achievement,
    format_featured_category,
    format_friend,
    format_game_details,
    format_game_schema,
    format_news_item,
    format_owned_game,
    format_package_details,
    format_player_bans,
    format_player_summary,
    format_review,
    format_wishlist_item,
)


class TestStripHtml:
    def test_removes_tags(self):
        assert _strip_html("<b>bold</b>") == "bold"

    def test_br_to_newline(self):
        assert _strip_html("line1<br>line2") == "line1\nline2"
        assert _strip_html("line1<br/>line2") == "line1\nline2"
        assert _strip_html("line1<BR />line2") == "line1\nline2"

    def test_decodes_entities(self):
        assert _strip_html("A &amp; B &lt; C &gt; D") == "A & B < C > D"
        assert _strip_html("it&#39;s &quot;fine&quot;") == 'it\'s "fine"'

    def test_strips_whitespace(self):
        assert _strip_html("  hello  ") == "hello"

    def test_empty_string(self):
        assert _strip_html("") == ""


class TestFormatOwnedGame:
    def test_basic(self):
        result = format_owned_game(
            {
                "name": "Portal 2",
                "appid": 620,
                "playtime_forever": 125,
            }
        )
        assert result["name"] == "Portal 2"
        assert result["appid"] == 620
        assert result["playtime_total"] == "2h 5m"
        assert "playtime_2weeks" not in result
        assert "last_played" not in result

    def test_with_recent_playtime(self):
        result = format_owned_game(
            {
                "name": "Test",
                "appid": 1,
                "playtime_forever": 60,
                "playtime_2weeks": 30,
            }
        )
        assert result["playtime_2weeks"] == "30m"

    def test_with_last_played(self):
        result = format_owned_game(
            {
                "name": "Test",
                "appid": 1,
                "playtime_forever": 0,
                "rtime_last_played": 1700000000,
            }
        )
        assert "last_played" in result

    def test_zero_last_played_excluded(self):
        result = format_owned_game(
            {
                "name": "Test",
                "appid": 1,
                "playtime_forever": 0,
                "rtime_last_played": 0,
            }
        )
        assert "last_played" not in result


class TestFormatGameDetails:
    def test_basic_paid_game(self):
        result = format_game_details(
            {
                "name": "Half-Life 2",
                "steam_appid": 220,
                "type": "game",
                "is_free": False,
                "short_description": "A classic FPS.",
                "price_overview": {
                    "final_formatted": "$9.99",
                    "discount_percent": 0,
                },
                "genres": [{"description": "Action"}, {"description": "FPS"}],
                "platforms": {"windows": True, "mac": True, "linux": False},
                "release_date": {"date": "Nov 16, 2004", "coming_soon": False},
            }
        )
        assert result["name"] == "Half-Life 2"
        assert result["price"] == "$9.99"
        assert "discount_percent" not in result
        assert result["genres"] == ["Action", "FPS"]
        assert result["platforms"] == ["windows", "mac"]

    def test_discounted(self):
        result = format_game_details(
            {
                "name": "Test",
                "price_overview": {
                    "final_formatted": "$4.99",
                    "discount_percent": 50,
                },
            }
        )
        assert result["discount_percent"] == 50

    def test_free_game(self):
        result = format_game_details({"name": "TF2", "is_free": True})
        assert result["price"] == "Free"

    def test_metacritic(self):
        result = format_game_details(
            {
                "name": "Test",
                "metacritic": {"score": 92},
            }
        )
        assert result["metacritic_score"] == 92


class TestFormatAchievement:
    def test_unlocked(self):
        result = format_achievement(
            {
                "apiname": "ACH_001",
                "achieved": 1,
                "unlocktime": 1700000000,
            }
        )
        assert result["name"] == "ACH_001"
        assert result["achieved"] is True
        assert "unlocked_at" in result

    def test_locked(self):
        result = format_achievement({"apiname": "ACH_002", "achieved": 0})
        assert result["achieved"] is False
        assert "unlocked_at" not in result

    def test_with_global_percent(self):
        result = format_achievement(
            {"apiname": "ACH_001", "achieved": 0},
            global_percentages={"ACH_001": "45.678"},
        )
        assert result["global_percent"] == 45.7

    def test_without_global_percent(self):
        result = format_achievement({"apiname": "ACH_001", "achieved": 0})
        assert "global_percent" not in result


class TestFormatPlayerSummary:
    def test_online(self):
        result = format_player_summary(
            {
                "personaname": "TestUser",
                "steamid": "123",
                "personastate": 1,
                "profileurl": "https://example.com",
            }
        )
        assert result["name"] == "TestUser"
        assert result["status"] == "online"
        assert "currently_playing" not in result

    def test_playing_game(self):
        result = format_player_summary(
            {
                "personaname": "Gamer",
                "steamid": "123",
                "personastate": 1,
                "profileurl": "",
                "gameextrainfo": "Portal 2",
            }
        )
        assert result["currently_playing"] == "Portal 2"

    def test_all_statuses(self):
        expected = {
            0: "offline",
            1: "online",
            2: "busy",
            3: "away",
            4: "snooze",
            5: "looking to trade",
            6: "looking to play",
            99: "unknown",
        }
        for state, label in expected.items():
            result = format_player_summary(
                {
                    "personaname": "",
                    "steamid": "",
                    "personastate": state,
                    "profileurl": "",
                }
            )
            assert result["status"] == label


class TestFormatNewsItem:
    def test_basic(self):
        result = format_news_item(
            {
                "title": "Update 1.0",
                "author": "Dev",
                "contents": "Patch notes here.",
                "url": "https://example.com",
                "date": 1700000000,
            }
        )
        assert result["title"] == "Update 1.0"
        assert "date" in result

    def test_truncates_long_content(self):
        result = format_news_item(
            {
                "title": "",
                "author": "",
                "contents": "x" * 600,
                "url": "",
            }
        )
        assert len(result["contents"]) == 503  # 500 + "..."


class TestFormatWishlistItem:
    def test_with_price(self):
        result = format_wishlist_item(
            "730",
            {
                "name": "CS2",
                "priority": 1,
                "subs": [{"price": 1499, "discount_pct": 0}],
                "added": 1700000000,
            },
        )
        assert result["name"] == "CS2"
        assert result["appid"] == 730
        assert result["price"] == "$14.99"
        assert "discount_percent" not in result
        assert "added_at" in result

    def test_with_discount(self):
        result = format_wishlist_item(
            "1",
            {
                "name": "Test",
                "subs": [{"price": 999, "discount_pct": 50}],
            },
        )
        assert result["discount_percent"] == 50


class TestFormatFriend:
    def test_basic(self):
        result = format_friend(
            {
                "steamid": "123",
                "relationship": "friend",
                "friend_since": 1700000000,
            }
        )
        assert result["steamid"] == "123"
        assert "friends_since" in result

    def test_no_friend_since(self):
        result = format_friend({"steamid": "123", "relationship": "friend"})
        assert "friends_since" not in result


class TestFormatPlayerBans:
    def test_clean_record(self):
        result = format_player_bans(
            {
                "SteamId": "123",
                "CommunityBanned": False,
                "VACBanned": False,
                "NumberOfVACBans": 0,
                "DaysSinceLastBan": 0,
                "NumberOfGameBans": 0,
                "EconomyBan": "none",
            }
        )
        assert result["vac_banned"] is False
        assert result["vac_bans"] == 0

    def test_banned(self):
        result = format_player_bans(
            {
                "SteamId": "456",
                "VACBanned": True,
                "NumberOfVACBans": 2,
                "DaysSinceLastBan": 100,
            }
        )
        assert result["vac_banned"] is True
        assert result["vac_bans"] == 2


class TestFormatGameSchema:
    def test_with_achievements_and_stats(self):
        result = format_game_schema(
            {
                "gameName": "Test Game",
                "availableGameStats": {
                    "achievements": [
                        {
                            "name": "ACH_1",
                            "displayName": "First Blood",
                            "description": "Get your first kill",
                            "hidden": 0,
                        },
                        {
                            "name": "ACH_2",
                            "displayName": "Secret",
                            "hidden": 1,
                        },
                    ],
                    "stats": [
                        {"name": "kills", "displayName": "Total Kills"},
                    ],
                },
            }
        )
        assert result["game"] == "Test Game"
        assert result["achievement_count"] == 2
        assert result["stat_count"] == 1
        assert result["achievements"][1]["hidden"] is True
        assert "hidden" not in result["achievements"][0]

    def test_empty_schema(self):
        result = format_game_schema({"gameName": "Empty"})
        assert "achievements" not in result
        assert "stats" not in result


class TestFormatReview:
    def test_basic(self):
        result = format_review(
            {
                "voted_up": True,
                "review": "Great game!",
                "author": {"playtime_at_review": 120},
                "votes_up": 5,
                "votes_funny": 1,
                "timestamp_created": 1700000000,
            }
        )
        assert result["recommended"] is True
        assert result["text"] == "Great game!"
        assert result["playtime_at_review"] == "2h"
        assert "date" in result

    def test_strips_html(self):
        result = format_review(
            {
                "review": "<b>Bold</b> &amp; <i>italic</i>",
                "author": {},
            }
        )
        assert result["text"] == "Bold & italic"

    def test_truncates_long_review(self):
        result = format_review(
            {
                "review": "a" * 600,
                "author": {},
            }
        )
        assert len(result["text"]) == 503


class TestFormatFeaturedCategory:
    def test_basic(self):
        result = format_featured_category(
            {
                "name": "Top Sellers",
                "items": [
                    {
                        "name": "Game A",
                        "id": 100,
                        "discounted": True,
                        "discount_percent": 50,
                        "final_price": 999,
                        "original_price": 1999,
                    },
                    {
                        "name": "Game B",
                        "id": 200,
                        "discounted": False,
                        "final_price": 2999,
                    },
                ],
            }
        )
        assert result["name"] == "Top Sellers"
        assert result["count"] == 2
        assert result["items"][0]["discount_percent"] == 50
        assert result["items"][0]["price"] == "$9.99"
        assert result["items"][1]["price"] == "$29.99"

    def test_free_game(self):
        result = format_featured_category(
            {
                "name": "Free",
                "items": [
                    {"name": "F2P", "id": 1, "discounted": False, "free": True},
                ],
            }
        )
        assert result["items"][0]["price"] == "Free"


class TestFormatPackageDetails:
    def test_basic(self):
        result = format_package_details(
            {
                "name": "Valve Complete Pack",
                "price": {
                    "final": 4999,
                    "initial": 9999,
                    "discount_percent": 50,
                },
                "apps": [
                    {"id": 220, "name": "Half-Life 2"},
                    {"id": 620, "name": "Portal 2"},
                ],
                "platforms": {"windows": True, "mac": True, "linux": False},
                "release_date": {"date": "Sep 24, 2008"},
            }
        )
        assert result["name"] == "Valve Complete Pack"
        assert result["price"] == "$49.99"
        assert result["discount_percent"] == 50
        assert result["original_price"] == "$99.99"
        assert result["app_count"] == 2
        assert result["platforms"] == ["windows", "mac"]

    def test_no_discount(self):
        result = format_package_details(
            {
                "name": "Test",
                "price": {"final": 1999, "discount_percent": 0},
            }
        )
        assert "discount_percent" not in result
        assert "original_price" not in result
