"""
byceps.util.image.models
~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from enum import Enum
from typing import NamedTuple


class Dimensions(NamedTuple('Dimensions', ['width', 'height'])):
    """A 2D image's width and height."""

    __slots__ = ()

    @property
    def is_square(self) -> bool:
        return self.width == self.height


ImageType = Enum('ImageType', ['gif', 'jpeg', 'png', 'svg', 'webp'])
