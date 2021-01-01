"""
byceps.util.image.models
~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections import namedtuple
from enum import Enum


class Dimensions(namedtuple('Dimensions', ['width', 'height'])):
    """A 2D image's width and height."""

    __slots__ = ()

    @property
    def is_square(self) -> bool:
        return self.width == self.height


ImageType = Enum('ImageType', ['gif', 'jpeg', 'png', 'svg'])
