from __future__ import annotations


def parse_color_string(color: str) -> tuple[int, int, int]:
    """Parse an underscore-separated RGB string into a tuple.

    Args:
        color: Color encoded as 'R_G_B' (e.g. '255_128_0').

    Returns:
        RGB tuple of ints.

    Raises:
        ValueError: If the string is not a valid R_G_B triplet with components 0-255.
    """
    parts = color.split("_")
    if len(parts) != 3:
        raise ValueError(f"Expected R_G_B format, got: {color!r}")
    r, g, b = (int(p) for p in parts)
    if not all(0 <= v <= 255 for v in (r, g, b)):
        raise ValueError(f"Color components must be 0-255, got: {color!r}")
    return r, g, b


def hex_to_rgb_tuple(color: str) -> tuple[int, int, int]:
    """Convert a hex color string to an RGB tuple.

    Args:
        color: Hex color string, with or without leading '#' (e.g. '#FF8000').

    Returns:
        RGB tuple of ints.

    Raises:
        ValueError: If the string is not a valid 6-digit hex color.
    """
    color = color.lstrip("#")
    if len(color) != 6:
        raise ValueError(f"Expected 6-digit hex color, got: {color!r}")
    return (int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16))
