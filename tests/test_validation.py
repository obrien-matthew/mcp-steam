import pytest

from steam_mcp.validation import (
    format_playtime,
    validate_app_id,
    validate_limit,
    validate_steam_id,
)


class TestValidateAppId:
    def test_valid_string(self):
        assert validate_app_id("730") == 730

    def test_valid_int(self):
        assert validate_app_id(730) == 730

    def test_whitespace_padded(self):
        assert validate_app_id(" 730 ") == 730

    def test_zero_raises(self):
        with pytest.raises(ValueError, match="Must be positive"):
            validate_app_id(0)

    def test_negative_raises(self):
        with pytest.raises(ValueError, match="Must be positive"):
            validate_app_id(-1)

    def test_non_numeric_raises(self):
        with pytest.raises(ValueError, match="Expected a numeric"):
            validate_app_id("abc")

    def test_empty_string_raises(self):
        with pytest.raises(ValueError, match="Expected a numeric"):
            validate_app_id("")


class TestValidateLimit:
    def test_within_range(self):
        assert validate_limit(10) == 10

    def test_below_min_clamps(self):
        assert validate_limit(0) == 1
        assert validate_limit(-5) == 1

    def test_above_max_clamps(self):
        assert validate_limit(100) == 50

    def test_custom_max(self):
        assert validate_limit(30, max_val=25) == 25
        assert validate_limit(10, max_val=25) == 10


class TestValidateSteamId:
    def test_valid_17_digit(self):
        assert validate_steam_id("76561198015781444") == "76561198015781444"

    def test_strips_whitespace(self):
        assert validate_steam_id(" 76561198015781444 ") == "76561198015781444"

    def test_too_short_raises(self):
        with pytest.raises(ValueError, match="Invalid Steam ID"):
            validate_steam_id("12345")

    def test_non_numeric_raises(self):
        with pytest.raises(ValueError, match="Invalid Steam ID"):
            validate_steam_id("gabelogannewell")


class TestFormatPlaytime:
    def test_zero(self):
        assert format_playtime(0) == "0m"

    def test_minutes_only(self):
        assert format_playtime(45) == "45m"

    def test_exact_hours(self):
        assert format_playtime(120) == "2h"

    def test_hours_and_minutes(self):
        assert format_playtime(125) == "2h 5m"

    def test_one_hour(self):
        assert format_playtime(60) == "1h"
