"""
byceps.services.image.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import BinaryIO, FrozenSet, Iterable, Set

from ...util.image import read_dimensions
from ...util.image.models import Dimensions, ImageType
from ...util.image.typeguess import guess_type


class ImageTypeProhibited(ValueError):
    pass


def get_image_type_names(types: Iterable[ImageType]) -> FrozenSet[str]:
    """Return the names of the image types."""
    return frozenset(t.name.upper() for t in types)


def determine_image_type(
    stream: BinaryIO, allowed_types: Set[ImageType]
) -> ImageType:
    """Extract image type from stream."""
    image_type = guess_type(stream)

    if image_type not in allowed_types:
        allowed_type_names = get_image_type_names(allowed_types)
        allowed_type_names_string = ', '.join(sorted(allowed_type_names))

        raise ImageTypeProhibited(
            'Image is not one of the allowed types ({}).'
            .format(allowed_type_names_string))

    stream.seek(0)
    return image_type


def determine_dimensions(stream: BinaryIO) -> Dimensions:
    """Extract image dimensions from stream."""
    dimensions = read_dimensions(stream)
    stream.seek(0)
    return dimensions
