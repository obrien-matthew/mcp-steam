# Steam Web API Endpoints Research

Research date: 2026-04-03

## Currently Implemented (12 tools)

| # | Tool | Endpoint |
|---|------|----------|
| 1 | get_player_summary | ISteamUser/GetPlayerSummaries/v2 |
| 2 | get_friend_list | ISteamUser/GetFriendList/v1 |
| 3 | get_owned_games | IPlayerService/GetOwnedGames/v1 |
| 4 | get_recently_played | IPlayerService/GetRecentlyPlayedGames/v1 |
| 5 | get_achievements | ISteamUserStats/GetPlayerAchievements/v1 |
| 6 | get_global_achievement_stats | ISteamUserStats/GetGlobalAchievementPercentagesForApp/v2 |
| 7 | get_player_stats | ISteamUserStats/GetUserStatsForGame/v2 |
| 8 | get_game_details | store.steampowered.com/api/appdetails |
| 9 | get_game_news | ISteamNews/GetNewsForApp/v2 |
| 10 | get_wishlist | store.steampowered.com/wishlist/profiles/{id}/wishlistdata |
| 11 | get_featured_games | store.steampowered.com/api/featured |
| 12 | search_games | store.steampowered.com/api/storesearch |

---

## Available Endpoints NOT Yet Implemented

### HIGH Usefulness

#### 1. Resolve Vanity URL
- **Endpoint:** `ISteamUser/ResolveVanityURL/v1/`
- **Description:** Converts a Steam custom profile URL name (vanity URL) to a 64-bit Steam ID. Essential for letting users look up other players by username instead of needing to know their numeric Steam ID.
- **Requires API Key:** Yes
- **Why HIGH:** Enables all player-lookup tools to accept vanity names (e.g., "gabelogannewell") instead of requiring raw Steam IDs. This is a force multiplier for every existing player-related tool.

#### 2. Get Current Player Count
- **Endpoint:** `ISteamUserStats/GetNumberOfCurrentPlayers/v1/`
- **Description:** Returns the number of players currently playing a specific game on Steam.
- **Requires API Key:** No (works without a key)
- **Why HIGH:** Very commonly requested data point. "How many people are playing X right now?" is a natural question for an MCP user.

#### 3. Get Game Schema (Achievement/Stat Definitions)
- **Endpoint:** `ISteamUserStats/GetSchemaForGame/v2/`
- **Description:** Returns the complete list of achievements and stats for a game, including display names, descriptions, hidden status, and icon URLs (earned and unearned).
- **Requires API Key:** Yes
- **Why HIGH:** Enriches existing achievement tools with human-readable names, descriptions, and icons. Currently `get_achievements` returns API names only; this provides the display metadata.

#### 4. Get Player Bans
- **Endpoint:** `ISteamUser/GetPlayerBans/v1/`
- **Description:** Returns ban information (VAC bans, community bans, game bans, economy bans) for one or more Steam IDs.
- **Requires API Key:** Yes
- **Why HIGH:** Common use case for checking player reputation. Useful for community moderation or just curiosity.

#### 5. Get Steam Level
- **Endpoint:** `IPlayerService/GetSteamLevel/v1/`
- **Description:** Returns the Steam Level of a user.
- **Requires API Key:** Yes
- **Why HIGH:** Simple, fast, and commonly requested. Complements `get_player_summary` nicely.

#### 6. Get Badges
- **Endpoint:** `IPlayerService/GetBadges/v1/`
- **Description:** Returns all badges owned by a user, including badge level, XP earned, scarcity (how many users have it), and foil status. Also returns the user's overall Steam level and XP.
- **Requires API Key:** Yes
- **Why HIGH:** Rich profile data showing engagement/collecting progress. Pairs well with Steam Level.

#### 7. Get App Reviews
- **Endpoint:** `store.steampowered.com/appreviews/{appid}?json=1`
- **Description:** Returns user reviews for a game with filtering by review type (positive/negative), purchase type (Steam/non-Steam), language, and more. Supports pagination with cursor.
- **Requires API Key:** No
- **Why HIGH:** Reviews are one of the most important signals for game quality. Enables "what do people think of this game?" queries.

---

### MEDIUM Usefulness

#### 8. Get Player Summaries (Multi-User)
- **Endpoint:** `ISteamUser/GetPlayerSummaries/v2/` (already implemented, but only for self)
- **Description:** The existing endpoint supports up to 100 comma-separated Steam IDs. Extending the current tool to accept an optional steam_id parameter would allow looking up any player.
- **Requires API Key:** Yes
- **Why MEDIUM:** Not a new endpoint but a capability extension. Combined with ResolveVanityURL, this becomes very powerful.

#### 9. Get User Group List
- **Endpoint:** `ISteamUser/GetUserGroupList/v1/`
- **Description:** Returns all groups a Steam account belongs to (community groups and game groups).
- **Requires API Key:** Yes
- **Why MEDIUM:** Niche but useful for understanding a player's community involvement.

#### 10. Get Community Badge Progress
- **Endpoint:** `IPlayerService/GetCommunityBadgeProgress/v1/`
- **Description:** Returns all quests needed for a specific badge and which are completed.
- **Requires API Key:** Yes
- **Why MEDIUM:** Useful for badge completionists, but fairly niche.

#### 11. Get Featured Categories
- **Endpoint:** `store.steampowered.com/api/featuredcategories/`
- **Description:** Returns games featured on the Steam storefront organized by category (Top Sellers, New Releases, Specials, Coming Soon, etc.).
- **Requires API Key:** No
- **Why MEDIUM:** Broader than `get_featured_games`. Good for "what's on sale?" or "what's new?" queries, but overlaps with the existing featured tool.

#### 12. Get Package Details
- **Endpoint:** `store.steampowered.com/api/packagedetails/?packageids={id}`
- **Description:** Returns details about a Steam package/bundle including price, apps included, platforms, and release date.
- **Requires API Key:** No
- **Why MEDIUM:** Useful for bundle/package price comparisons, but most users think in terms of apps not packages.

#### 13. Get App List (Full Catalog)
- **Endpoint:** `IStoreService/GetAppList/v1/`
- **Description:** Returns a paginated list of all apps on Steam. Filterable by type (games, DLC, software, videos, hardware). Returns up to 50,000 per request.
- **Requires API Key:** Yes
- **Why MEDIUM:** Useful for catalog browsing or building a local index, but the response is massive and not directly useful in a conversational MCP context without further filtering.

#### 14. Is Playing Shared Game
- **Endpoint:** `IPlayerService/IsPlayingSharedGame/v1/`
- **Description:** Returns the original owner's Steam ID if a borrower is currently playing a shared game. Returns 0 otherwise.
- **Requires API Key:** Yes
- **Why MEDIUM:** Niche use case for Family Sharing users.

#### 15. Get Global Stats for Game
- **Endpoint:** `ISteamUserStats/GetGlobalStatsForGame/v1/`
- **Description:** Returns aggregated global stats (not achievements) for a game, such as total kills, total hours played globally, etc. Supports historical data with date ranges.
- **Requires API Key:** Yes
- **Why MEDIUM:** Interesting for games that expose global stat counters, but not all games use this feature.

---

### LOW Usefulness

#### 16. Get Supported API List
- **Endpoint:** `ISteamWebAPIUtil/GetSupportedAPIList/v1/`
- **Description:** Returns the complete list of all available API interfaces/methods accessible with the provided key.
- **Requires API Key:** Optional (shows more with key)
- **Why LOW:** Meta/debugging tool, not useful for end users.

#### 17. Get Server Info
- **Endpoint:** `ISteamWebAPIUtil/GetServerInfo/v1/`
- **Description:** Returns Steam Web API server time and other server info.
- **Requires API Key:** No
- **Why LOW:** No practical use for MCP users.

#### 18. Get App List (Deprecated)
- **Endpoint:** `ISteamApps/GetAppList/v2/`
- **Description:** Deprecated in favor of IStoreService/GetAppList. Returns basic app ID + name pairs.
- **Requires API Key:** No
- **Why LOW:** Deprecated. Use IStoreService/GetAppList instead.

#### 19. App User Details
- **Endpoint:** `store.steampowered.com/api/appuserdetails/?appids={id}`
- **Description:** Returns user-specific details for an app (ownership status, etc.). Requires authentication cookies, not just API key.
- **Requires API Key:** Requires Steam login cookies
- **Why LOW:** Requires browser-level auth, not suitable for API key-based access.

---

## Recommended Implementation Priority

### Phase 1 (Highest Impact, Lowest Effort)
1. **resolve_vanity_url** - Unlocks player lookup by name for all tools
2. **get_current_players** - Simple, no API key needed, high value
3. **get_steam_level** - One-liner, complements profile data
4. **get_player_bans** - Simple, commonly requested

### Phase 2 (High Value, Moderate Effort)
5. **get_game_schema** - Enriches achievement display significantly
6. **get_badges** - Rich profile/engagement data
7. **get_app_reviews** - Reviews are critical game info

### Phase 3 (Nice to Have)
8. **get_featured_categories** - Extends store browsing
9. **get_package_details** - Bundle/package info
10. Extend existing tools to accept arbitrary Steam IDs (not just self)

---

## Sources

- [Steamworks Web API Reference](https://partner.steamgames.com/doc/webapi)
- [ISteamUser Interface](https://partner.steamgames.com/doc/webapi/isteamuser)
- [IPlayerService Interface](https://partner.steamgames.com/doc/webapi/iplayerservice)
- [ISteamUserStats Interface](https://partner.steamgames.com/doc/webapi/ISteamUserStats)
- [ISteamApps Interface](https://partner.steamgames.com/doc/webapi/isteamapps)
- [IStoreService Interface](https://partner.steamgames.com/doc/webapi/IStoreService)
- [Steam Web API Documentation (xPaw)](https://steamapi.xpaw.me/)
- [Storefront API (TF2 Wiki)](https://wiki.teamfortress.com/wiki/User:RJackson/StorefrontAPI)
- [Steam Store Reviews API](https://partner.steamgames.com/doc/store/getreviews)
- [Better Steam Web API Documentation](https://steamwebapi.azurewebsites.net/)
