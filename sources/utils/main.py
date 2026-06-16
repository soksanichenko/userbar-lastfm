from __future__ import annotations

import logging
import os
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont

from config import LASTFM_API_KEY, PATH_TO_FONT
from sources.main import lastfm_app

from sources.utils.api import LastFmException, User

logger = logging.getLogger(__name__)

RGBColor = tuple[int, int, int]


def user_get_last_track(username: str) -> dict | str:
    """Fetch the most recent (or currently playing) track for a Last.fm user.

    Args:
        username: Last.fm username.

    Returns:
        Dict with track info, or a string error/status message.
    """
    result = None
    last_track: dict | str | None = None
    user = User(LASTFM_API_KEY, username=username)
    try:
        result = user.user_get_recent_tracks(extended=1)
        result = result['recent_tracks']
    except LastFmException as error:
        last_track = error.message

    if not result and not last_track:
        last_track = 'Not recent tracks'
    elif isinstance(result, list):
        playing = [track for track in result if track.get('now_playing')]
        last_track = dict((playing or result)[0])

    return last_track or 'No recent tracks'  # type: ignore[return-value]


def _interpolate(f_co: RGBColor, t_co: RGBColor, steps: int):
    """Yield interpolated RGB color tuples between f_co and t_co."""
    det_co = [(t - f) / steps for f, t in zip(f_co, t_co)]
    for i in range(steps):
        yield tuple(round(f + det * i) for f, det in zip(f_co, det_co))


def gradient(inner_color: RGBColor, outer_color: RGBColor,
             border_color: RGBColor | None = None, width: int = 350) -> BytesIO:
    """Render a horizontal gradient image and return it as a BytesIO PNG.

    Args:
        inner_color: Left-side gradient colour (RGB tuple).
        outer_color: Right-side gradient colour (RGB tuple).
        border_color: Optional border colour; draws a 2-px framed border.
        width: Image width in pixels.

    Returns:
        BytesIO containing the PNG image, seeked to position 0.
    """
    img = Image.new('RGBA', (width, 23), color=0)
    draw = ImageDraw.Draw(img)

    for i, color in enumerate(_interpolate(inner_color, outer_color, img.width)):
        draw.line([(i, 0), (i, img.height)], tuple(color), width=1)

    if border_color is not None:
        inv = tuple(255 - c for c in border_color)
        w, h = img.width - 1, img.height - 1
        draw.line([(0, 0), (w, 0)], border_color, width=1)
        draw.line([(0, h), (w, h)], border_color, width=1)
        draw.line([(0, 0), (0, h)], border_color, width=1)
        draw.line([(w, 0), (w, h)], border_color, width=1)
        draw.line([(1, 1), (w - 1, 1)], inv, width=1)
        draw.line([(1, h - 1), (w - 1, h - 1)], inv, width=1)
        draw.line([(1, 1), (1, h - 1)], inv, width=1)
        draw.line([(w - 1, 1), (w - 1, h - 1)], inv, width=1)

    out = BytesIO()
    img.save(out, 'PNG')
    out.seek(0)
    return out


def paste_text(text: str, text_color: RGBColor, inner_color: RGBColor,
               outer_color: RGBColor, border_color: RGBColor | None,
               truncate_text: bool = False) -> BytesIO:
    """Render text onto a gradient background and return it as a BytesIO PNG.

    Args:
        text: Text string to draw.
        text_color: Text colour (RGB tuple).
        inner_color: Left-side gradient colour.
        outer_color: Right-side gradient colour.
        border_color: Optional border colour.
        truncate_text: Cap bar width at 750 px and truncate text to 95 chars.

    Returns:
        BytesIO containing the PNG image, seeked to position 0.
    """
    default_width = 305
    max_width = 750
    logo_margin = 70
    trunc_len = 95
    x, y = 10, 2

    font_path = os.path.join(lastfm_app.static_folder, PATH_TO_FONT)
    font = ImageFont.truetype(font_path, 14, encoding='utf-8')

    probe = Image.new('RGBA', (1, 1))

    if truncate_text:
        text = '{}...'.format(text[:trunc_len]) if len(text) > trunc_len else text
        text_width = int(ImageDraw.Draw(probe).textlength(text, font=font))
        bar_width = min(max_width, logo_margin + text_width)
    else:
        text_width = int(ImageDraw.Draw(probe).textlength(text, font=font))
        bar_width = max(default_width, logo_margin + text_width)

    in_img = gradient(inner_color, outer_color, border_color, width=bar_width)
    img = Image.open(in_img)
    ImageDraw.Draw(img).text((x, y), text, font=font, fill=text_color)

    out = BytesIO()
    img.save(out, 'PNG')
    out.seek(0)
    return out


def paste_logo(in_img: BytesIO, logo_color: RGBColor | None = None) -> BytesIO:
    """Paste a recoloured logo onto the right edge of the image.

    Args:
        in_img: BytesIO source image.
        logo_color: Target colour for logo pixels; if None, returns in_img unchanged.

    Returns:
        BytesIO containing the composited PNG, seeked to position 0.
    """
    if logo_color is None:
        return in_img

    logo = Image.open(os.path.join(lastfm_app.static_folder, 'logo.png'))
    for lx in range(logo.size[0]):
        for ly in range(logo.size[1]):
            pixel = logo.getpixel((lx, ly))
            if pixel[3] > 0:
                logo.putpixel((lx, ly), (*logo_color, pixel[3]))

    in_img.seek(0)
    img = Image.open(in_img)
    img.paste(logo, (img.width - 40, 3), logo)

    out = BytesIO()
    img.save(out, 'PNG')
    out.seek(0)
    return out


def make_userbar_text(text_format: str = '{artist_name} - {track_name}', **kwargs: object) -> str:
    """Format the userbar text string from track metadata.

    Args:
        text_format: Template string with named placeholders.
        **kwargs: Track metadata fields (artist_name, track_name, etc.).

    Returns:
        Formatted userbar text.
    """
    return text_format.format(**kwargs)


def create_userbar(username: str, inner_color: RGBColor, outer_color: RGBColor,
                   text_color: RGBColor, border_color: RGBColor | None = None,
                   logo_color: RGBColor | None = None, truncate_text: bool = False) -> BytesIO:
    """Build a complete Last.fm userbar image for the given user.

    Args:
        username: Last.fm username.
        inner_color: Left-side gradient colour.
        outer_color: Right-side gradient colour.
        text_color: Text colour.
        border_color: Optional border colour.
        logo_color: Optional logo colour; if None, no logo is drawn.
        truncate_text: Cap bar width at 750 px.

    Returns:
        BytesIO containing the PNG image, seeked to position 0.
    """
    result = user_get_last_track(username=username)
    text = make_userbar_text(**result) if isinstance(result, dict) else result
    logger.info('userbar text: %s', text)

    img = paste_text(text, text_color, inner_color, outer_color, border_color, truncate_text)
    img.seek(0)
    if logo_color is not None:
        img = paste_logo(img, logo_color)
    return img
