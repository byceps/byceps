"""
byceps.services.gallery.gallery_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.services.brand.models import BrandID
from byceps.util.result import Result

from . import gallery_domain_service, gallery_repository
from .dbmodels import DbGallery, DbGalleryImage
from .errors import GalleryAlreadyAtBottomError, GalleryAlreadyAtTopError
from .models import (
    Gallery,
    GalleryID,
    GalleryImage,
    GalleryImageID,
    GalleryWithImages,
)


# -------------------------------------------------------------------- #
# gallery


def create_gallery(
    brand_id: BrandID,
    slug: str,
    title: str,
    hidden: bool,
) -> Gallery:
    """Create a gallery."""
    gallery = gallery_domain_service.create_gallery(
        brand_id, slug, title, hidden
    )

    gallery_repository.create_gallery(gallery)

    return gallery


def update_gallery(
    gallery: Gallery, slug: str, title: str, hidden: bool
) -> Gallery:
    """Update a gallery."""
    gallery = gallery_domain_service.update_gallery(
        gallery, slug, title, hidden
    )

    gallery_repository.update_gallery(gallery)

    return gallery


def move_gallery_up(gallery: Gallery) -> Result[None, GalleryAlreadyAtTopError]:
    """Move a gallery upwards by one position."""
    return gallery_repository.move_gallery_up(gallery.id)


def move_gallery_down(
    gallery: Gallery,
) -> Result[None, GalleryAlreadyAtBottomError]:
    """Move a gallery downwards by one position."""
    return gallery_repository.move_gallery_down(gallery.id)


def set_gallery_title_image(
    gallery_id: GalleryID, image_id: GalleryImageID
) -> None:
    """Set a title image for the gallery."""
    gallery_repository.set_gallery_title_image(gallery_id, image_id)


def remove_gallery_title_image(gallery_id: GalleryID) -> None:
    """Remove the title image for the gallery."""
    gallery_repository.remove_gallery_title_image(gallery_id)


def delete_gallery(gallery_id: GalleryID) -> None:
    """Delete a gallery from the database, but not the image files."""
    gallery_repository.delete_gallery(gallery_id)


def find_gallery(gallery_id: GalleryID) -> Gallery | None:
    """Return the gallery, if found."""
    db_gallery = gallery_repository.find_gallery(gallery_id)

    if db_gallery is None:
        return None

    return _db_entity_to_gallery(db_gallery)


def find_gallery_by_slug(brand_id: BrandID, slug: str) -> Gallery | None:
    """Return the gallery of that brand and with that slug, if found."""
    db_gallery = gallery_repository.find_gallery_by_slug(brand_id, slug)

    if db_gallery is None:
        return None

    return _db_entity_to_gallery(db_gallery)


def find_gallery_by_slug_with_images(
    brand_id: BrandID, slug: str
) -> GalleryWithImages | None:
    """Return the gallery of that brand and with that slug, if found,
    with images.
    """
    db_gallery = gallery_repository.find_gallery_by_slug_with_images(
        brand_id, slug
    )

    if db_gallery is None:
        return None

    return _db_entity_to_gallery_with_images(db_gallery)


def is_slug_available(brand_id: BrandID, slug: str) -> bool:
    """Check if the slug is yet unused."""
    return gallery_repository.is_slug_available(brand_id, slug)


def get_galleries_for_brand(brand_id: BrandID) -> list[Gallery]:
    """Return all galeries for the brand."""
    db_galleries = gallery_repository.get_galleries_for_brand(brand_id)

    return [_db_entity_to_gallery(db_gallery) for db_gallery in db_galleries]


def get_galleries_for_brand_with_images(
    brand_id: BrandID,
) -> list[GalleryWithImages]:
    """Return all galeries for the brand, with images."""
    db_galleries = gallery_repository.get_galleries_for_brand_with_images(
        brand_id
    )

    return [
        _db_entity_to_gallery_with_images(db_gallery)
        for db_gallery in db_galleries
    ]


def _db_entity_to_gallery(db_gallery: DbGallery) -> Gallery:
    title_image = _find_title_image(db_gallery)

    return Gallery(
        id=db_gallery.id,
        created_at=db_gallery.created_at,
        brand_id=db_gallery.brand_id,
        position=db_gallery.position,
        slug=db_gallery.slug,
        title=db_gallery.title,
        title_image=title_image,
        hidden=db_gallery.hidden,
    )


def _db_entity_to_gallery_with_images(
    db_gallery: DbGallery,
) -> GalleryWithImages:
    title_image = _find_title_image(db_gallery)

    images = [
        _db_entity_to_image(db_image, db_gallery)
        for db_image in db_gallery.images
    ]
    images.sort(key=lambda image: image.position)

    return GalleryWithImages(
        id=db_gallery.id,
        created_at=db_gallery.created_at,
        brand_id=db_gallery.brand_id,
        position=db_gallery.position,
        slug=db_gallery.slug,
        title=db_gallery.title,
        title_image=title_image,
        hidden=db_gallery.hidden,
        images=images,
    )


# -------------------------------------------------------------------- #
# image


def create_image(
    gallery: Gallery,
    filename_full: str,
    filename_preview: str,
    *,
    caption: str | None = None,
    hidden: bool = False,
) -> GalleryImage:
    """Add an image to a gallery."""
    image = gallery_domain_service.create_image(
        gallery, filename_full, filename_preview, caption, hidden
    )

    gallery_repository.create_image(image)

    return image


def _db_entity_to_image(
    db_image: DbGalleryImage, db_gallery: DbGallery
) -> GalleryImage:
    return GalleryImage(
        id=db_image.id,
        created_at=db_image.created_at,
        brand_id=db_gallery.brand_id,
        gallery_id=db_image.gallery_id,
        gallery_slug=db_gallery.slug,
        position=db_image.position,
        filename_full=db_image.filename_full,
        filename_preview=db_image.filename_preview,
        caption=db_image.caption,
        hidden=db_image.hidden,
    )


def _find_title_image(db_gallery: DbGallery) -> GalleryImage | None:
    db_title_image = db_gallery.title_image
    if not db_title_image:
        return None

    return _db_entity_to_image(db_title_image, db_gallery)
