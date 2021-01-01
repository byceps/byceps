"""
byceps.util.image.typeguess
~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import BinaryIO, Optional

from .models import ImageType


# See: https://www.w3.org/Graphics/GIF/spec-gif89a.txt
GIF_SIGNATURE = b'GIF'
GIF_VERSIONS = frozenset([b'87a', b'89a'])

# See: https://en.wikipedia.org/wiki/JPEG#Syntax_and_structure
JPEG_MARKER_SOI = b'\xff\xd8'

# See: https://tools.ietf.org/html/rfc2083#page-11
PNG_SIGNATURE = b'\x89PNG\r\n\x1a\n'


def guess_type(stream: BinaryIO) -> Optional[ImageType]:
    """Return the guessed type, or `None` if the type could not be
    guessed or is not allowed (i.e. not a member of the enum).
    """
    header = stream.read(8)
    stream.seek(0)

    if (header[:3] == GIF_SIGNATURE) and (header[3:6] in GIF_VERSIONS):
        return ImageType.gif
    elif header[:8] == PNG_SIGNATURE:
        return ImageType.png
    elif header[:2] == JPEG_MARKER_SOI:
        return ImageType.jpeg

    if _is_svg(stream):
        return ImageType.svg

    return None


def _is_svg(stream: BinaryIO) -> bool:
    header = stream.read(80)
    stream.seek(0)

    return header.startswith(b'<svg') or (
        header.startswith(b'<?xml version="1.0"') and header.find(b'<svg')
    )
