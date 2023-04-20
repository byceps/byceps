"""
byceps.util.image.typeguess
~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from typing import BinaryIO

from .models import ImageType


def guess_type(stream: BinaryIO) -> ImageType | None:
    """Return the guessed type, or `None` if the type could not be
    guessed or is not allowed (i.e. not a member of the enum).
    """
    header = stream.read(12)
    stream.seek(0)

    if _is_gif(header):
        return ImageType.gif
    elif _is_jpeg(header):
        return ImageType.jpeg
    elif _is_png(header):
        return ImageType.png
    elif _is_webp(header):
        return ImageType.webp

    if _is_svg(stream):
        return ImageType.svg

    return None


def _is_gif(header: bytes) -> bool:
    # See: https://www.w3.org/Graphics/GIF/spec-gif89a.txt
    return header[:6] in (b'GIF87a', b'GIF89a')


def _is_jpeg(header: bytes) -> bool:
    # See: https://en.wikipedia.org/wiki/JPEG#Syntax_and_structure
    jpeg_marker_soi = b'\xff\xd8'
    return header.startswith(jpeg_marker_soi)


def _is_png(header: bytes) -> bool:
    # See: https://tools.ietf.org/html/rfc2083#page-11
    return header.startswith(b'\x89PNG\r\n\x1a\n')


def _is_webp(header: bytes) -> bool:
    return header.startswith(b'RIFF') and header[8:12] == b'WEBP'


def _is_svg(stream: BinaryIO) -> bool:
    header = stream.read(80)
    stream.seek(0)

    return bool(
        header.startswith(b'<svg')
        or (header.startswith(b'<?xml version="1.0"') and header.find(b'<svg'))
    )
