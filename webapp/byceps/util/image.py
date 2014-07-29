# -*- coding: utf-8 -*-

"""
byceps.util.image
~~~~~~~~~~~~~~~~~

:copyright: 2006-2014 Jochen Kupperschmidt
"""

from collections import namedtuple
from enum import Enum
import imghdr

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
