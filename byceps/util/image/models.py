"""
byceps.util.image.models
~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from enum import Enum
from typing import NamedTuple


class Dimensions(NamedTuple):
    """A 2D image's width and height."""

    width: int
    height: int

    @property
    def is_square(self) -> bool:
        return self.width == self.height


ImageType = Enum('ImageType', ['gif', 'jpeg', 'png', 'svg', 'webp'])
