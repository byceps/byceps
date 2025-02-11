"""
byceps.util.image
~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from io import BytesIO
from typing import BinaryIO

from PIL import Image, ImageFile

from .dimensions import Dimensions


FilenameOrStream = str | BinaryIO


def create_thumbnail(
    filename_or_stream: FilenameOrStream,
    image_type: str,
    maximum_dimensions: Dimensions,
    *,
    force_square: bool = False,
) -> BinaryIO:
    """Create a thumbnail from the given image and return the result stream."""
    output_stream = BytesIO()

    image = Image.open(filename_or_stream)

    if force_square:
        image = _crop_to_square(image)

    image.thumbnail(maximum_dimensions, resample=Image.Resampling.LANCZOS)

    image.save(output_stream, format=image_type)

    output_stream.seek(0)
    return output_stream


def _crop_to_square(image: ImageFile) -> ImageFile:
    """Crop image to be square."""
    dimensions = Dimensions(*image.size)

    if dimensions.is_square:
        return image

    edge_length = min(*dimensions)
    crop_box = (0, 0, edge_length, edge_length)

    return image.crop(crop_box)
