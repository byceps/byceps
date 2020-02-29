"""
byceps.util.image.typeguess
~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
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


def guess_type(data: BinaryIO) -> Optional[ImageType]:
    """Return the guessed type, or `None` if the type could not be
    guessed or is not allowed (i.e. not a member of the enum).
    """
    header = data.read(8)
    stream.seek(0)

    if (header[:3] == GIF_SIGNATURE) and (header[3:6] in GIF_VERSIONS):
        return ImageType.gif
    elif header[:8] == PNG_SIGNATURE:
        return ImageType.png
    elif header[:2] == JPEG_MARKER_SOI:
        return ImageType.jpeg
    else:
        return None
