# -*- coding: utf-8 -*-

"""
byceps.util.image
~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from collections import namedtuple
from enum import Enum
from io import BytesIO

from PIL import Image


Dimensions = namedtuple('Dimensions', ['width', 'height'])


ImageType = Enum('ImageType', ['gif', 'jpeg', 'png'])


# See: https://www.w3.org/Graphics/GIF/spec-gif89a.txt
GIF_SIGNATURE = b'GIF'
GIF_VERSIONS = frozenset([b'87a', b'89a'])

# See: https://en.wikipedia.org/wiki/JPEG#Syntax_and_structure
JPEG_MARKER_SOI = b'\xff\xd8'

# See: https://tools.ietf.org/html/rfc2083#page-11
PNG_SIGNATURE = b'\x89PNG\r\n\x1a\n'



def guess_type(data):
    """Return the guessed type, or `None` if the type could not be
    guessed or is not allowed (i.e. not a member of the enum).
    """
    header = data.read(8)

    if (header[:3] == GIF_SIGNATURE) and (header[3:6] in GIF_VERSIONS):
        return ImageType.gif
    elif header[:8] == PNG_SIGNATURE:
        return ImageType.png
    elif header[:2] == JPEG_MARKER_SOI:
        return ImageType.jpeg
    else:
        return None


def read_dimensions(filename_or_stream):
    """Return the dimensions of the image."""
    image = Image.open(filename_or_stream)
    return Dimensions(*image.size)


def create_thumbnail(filename_or_stream, image_type, maximum_dimensions):
    """Create a thumbnail from the given image and return the result stream."""
    output_stream = BytesIO()

    image = Image.open(filename_or_stream)
    image.thumbnail(maximum_dimensions, resample=Image.ANTIALIAS)
    image.save(output_stream, format=image_type)

    output_stream.seek(0)
    return output_stream
