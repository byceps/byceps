"""
byceps.services.gallery.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import NewType
from uuid import UUID

from byceps.services.brand.models import BrandID


GalleryID = NewType('GalleryID', UUID)

GalleryImageID = NewType('GalleryImageID', UUID)


@dataclass(frozen=True)
class Gallery:
    id: GalleryID
    created_at: datetime
    brand_id: BrandID
    slug: str
    title: str
    title_image: GalleryImage | None
    position: int
    hidden: bool


@dataclass(frozen=True)
class GalleryImage:
    id: GalleryImageID
    created_at: datetime
    brand_id: BrandID
    gallery_id: GalleryID
    gallery_slug: str
    filename_full: str
    filename_preview: str
    caption: str | None
    position: int
    hidden: bool

    @property
    def _url_path_base(self) -> str:
        return f'/data/brands/{self.brand_id}/galleries/{self.gallery_slug}'

    @property
    def url_path_full(self) -> str:
        return f'{self._url_path_base}/{self.filename_full}'

    @property
    def url_path_preview(self) -> str:
        return f'{self._url_path_base}/{self.filename_preview}'


@dataclass(frozen=True)
class GalleryWithImages(Gallery):
    images: list[GalleryImage]
