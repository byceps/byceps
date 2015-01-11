# -*- coding: utf-8 -*-

"""
byceps.util.image
~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
"""

from collections import namedtuple
from enum import Enum
import imghdr
from io import BytesIO

from PIL import Image


Dimensions = namedtuple('Dimensions', ['width', 'height'])


ImageType = Enum('ImageType', ['gif', 'jpeg', 'png'])


def guess_type(data):
    """Return the guessed type, or `None` if the type could not be
    guessed or is not allowed (i.e. not a member of the enum).
    """
    type_str = imghdr.what(data)
    try:
        return ImageType[type_str]
    except KeyError:
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
