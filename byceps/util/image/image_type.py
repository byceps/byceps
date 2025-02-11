"""
byceps.util.image.image_type
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from enum import Enum


ImageType = Enum('ImageType', ['gif', 'jpeg', 'png', 'svg', 'webp'])
