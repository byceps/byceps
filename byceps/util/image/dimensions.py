"""
byceps.util.image.dimensions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import BinaryIO, NamedTuple

from PIL import Image


FilenameOrStream = str | BinaryIO


class Dimensions(NamedTuple):
    """A 2D image's width and height."""

    width: int
    height: int

    @property
    def is_square(self) -> bool:
        return self.width == self.height


def determine_dimensions(stream: BinaryIO) -> Dimensions:
    """Extract image dimensions from stream."""
    dimensions = read_dimensions(stream)
    stream.seek(0)  # Move cursor back to beginning of stream.
    return dimensions


def read_dimensions(filename_or_stream: FilenameOrStream) -> Dimensions:
    """Return the dimensions of the image."""
    image = Image.open(filename_or_stream)
    return Dimensions(*image.size)
