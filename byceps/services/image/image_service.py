"""
byceps.services.image.image_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import BinaryIO

from byceps.util.image.image_type import get_image_type_names, ImageType
from byceps.util.image.typeguess import guess_type
from byceps.util.result import Err, Ok, Result


def determine_image_type(
    stream: BinaryIO, allowed_types: frozenset[ImageType] | set[ImageType]
) -> Result[ImageType, str]:
    """Extract image type from stream."""
    image_type = guess_type(stream)

    if (image_type is None) or (image_type not in allowed_types):
        message = _get_image_type_prohibited_error_message(allowed_types)
        return Err(message)

    return Ok(image_type)


def _get_image_type_prohibited_error_message(
    allowed_types: frozenset[ImageType] | set[ImageType],
) -> str:
    allowed_type_names = get_image_type_names(allowed_types)
    allowed_type_names_string = ', '.join(sorted(allowed_type_names))

    return (
        f'Image is not one of the allowed types ({allowed_type_names_string}).'
    )
