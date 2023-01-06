"""
byceps.services.image.image_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from typing import BinaryIO, Iterable

from ...util.image import read_dimensions
from ...util.image.models import Dimensions, ImageType
from ...util.image.typeguess import guess_type


class ImageTypeProhibited(ValueError):
    pass


def get_image_type_names(types: Iterable[ImageType]) -> frozenset[str]:
    """Return the names of the image types."""
    return frozenset(t.name.upper() for t in types)


def determine_image_type(
    stream: BinaryIO, allowed_types: frozenset[ImageType] | set[ImageType]
) -> ImageType:
    """Extract image type from stream."""
    image_type = guess_type(stream)

    if (image_type is None) or (image_type not in allowed_types):
        allowed_type_names = get_image_type_names(allowed_types)
        allowed_type_names_string = ', '.join(sorted(allowed_type_names))

        raise ImageTypeProhibited(
            'Image is not one of the allowed types '
            f'({allowed_type_names_string}).'
        )

    return image_type


def determine_dimensions(stream: BinaryIO) -> Dimensions:
    """Extract image dimensions from stream."""
    dimensions = read_dimensions(stream)
    stream.seek(0)
    return dimensions
