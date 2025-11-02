"""
byceps.services.gallery.errors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class GalleryAlreadyAtBottomError:
    pass


@dataclass(frozen=True)
class GalleryAlreadyAtTopError:
    pass
