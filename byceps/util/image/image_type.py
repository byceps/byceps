"""
byceps.util.image.image_type
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Iterable
from enum import Enum


ImageType = Enum('ImageType', ['gif', 'jpeg', 'png', 'svg', 'webp'])


def get_image_type_names(types: Iterable[ImageType]) -> frozenset[str]:
    """Return the names of the image types."""
    return frozenset(t.name.upper() for t in types)
