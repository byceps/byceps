"""
byceps.util.image.dimensions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import NamedTuple


class Dimensions(NamedTuple):
    """A 2D image's width and height."""

    width: int
    height: int

    @property
    def is_square(self) -> bool:
        return self.width == self.height
