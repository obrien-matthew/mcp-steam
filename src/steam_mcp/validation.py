"""Input validation helpers for Steam app IDs and pagination parameters."""


def validate_app_id(value: str | int) -> int:
    """Validate and convert a Steam app ID to int."""
    if isinstance(value, int):
        if value <= 0:
            raise ValueError(f"Invalid app ID: {value}. Must be positive.")
        return value
    value_str = str(value).strip()
    if not value_str.isdigit():
        raise ValueError(f"Invalid app ID: '{value_str}'. Expected a numeric value.")
    result = int(value_str)
    if result <= 0:
        raise ValueError(f"Invalid app ID: {result}. Must be positive.")
    return result


def validate_limit(value: int, max_val: int = 50) -> int:
    """Clamp a limit parameter to the range [1, max_val]."""
    return max(1, min(value, max_val))


def validate_steam_id(value: str) -> str:
    """Validate a Steam 64-bit ID string."""
    value = value.strip()
    if not value.isdigit() or len(value) < 10:
        raise ValueError(
            f"Invalid Steam ID: '{value}'. Expected a 64-bit numeric ID "
            "(e.g. 76561198015781444). Use resolve_vanity_url to convert usernames."
        )
    return value


def format_playtime(minutes: int) -> str:
    """Convert playtime in minutes to a human-readable string."""
    if minutes < 60:
        return f"{minutes}m"
    hours = minutes // 60
    remaining = minutes % 60
    if remaining == 0:
        return f"{hours}h"
    return f"{hours}h {remaining}m"
