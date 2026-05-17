from __future__ import annotations


def parse_color_string(color: str) -> tuple[int, ...]:
    """Parse an underscore-separated RGB string into a tuple.

    Args:
        color: Color encoded as 'R_G_B' (e.g. '255_128_0').

    Returns:
        RGB tuple of ints.
    """
    return tuple(int(c) for c in color.split('_'))


def hex_to_rgb_string(color: str) -> str:
    """Convert a hex color string to underscore-separated RGB.

    Args:
        color: Hex color string, with or without leading '#' (e.g. '#FF8000').

    Returns:
        RGB encoded as 'R_G_B' (e.g. '255_128_0').
    """
    color = color.lstrip('#')
    return '_'.join(str(int(color[i:i + 2], 16)) for i in (0, 2, 4))


def hex_to_rgb_tuple(color: str) -> tuple[int, int, int]:
    """Convert a hex color string to an RGB tuple.

    Args:
        color: Hex color string, with or without leading '#' (e.g. '#FF8000').

    Returns:
        RGB tuple of ints.
    """
    color = color.lstrip('#')
    return (int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16))
