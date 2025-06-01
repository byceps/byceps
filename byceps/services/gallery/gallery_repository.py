"""
byceps.services.gallery.gallery_repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from sqlalchemy import select

from byceps.database import db
from byceps.services.brand import brand_service
from byceps.services.brand.models import BrandID

from .dbmodels import DbGallery, DbGalleryImage
from .models import Gallery, GalleryID, GalleryImage


# -------------------------------------------------------------------- #
# gallery


def create_gallery(gallery: Gallery) -> None:
    """Create a gallery."""
    brand_id = gallery.brand_id
    db_brand = brand_service._find_db_brand(brand_id)
    if db_brand is None:
        raise ValueError(f'Unknown brand ID "{brand_id}"')

    db_gallery = DbGallery(
        gallery.id,
        gallery.created_at,
        gallery.brand_id,
        gallery.slug,
        gallery.title,
        gallery.hidden,
    )
    db_brand.galleries.append(db_gallery)
    db.session.commit()


def update_gallery(gallery: Gallery) -> None:
    """Update a gallery."""
    db_gallery = get_gallery(gallery.id)

    db_gallery.slug = gallery.slug
    db_gallery.title = gallery.title
    db_gallery.hidden = gallery.hidden

    db.session.commit()


def find_gallery(gallery_id: GalleryID) -> DbGallery | None:
    """Return the gallery, if found."""
    return db.session.get(DbGallery, gallery_id)


def get_gallery(gallery_id: GalleryID) -> DbGallery:
    """Return the gallery."""
    db_gallery = find_gallery(gallery_id)

    if db_gallery is None:
        raise ValueError(f'Unknown gallery ID "{gallery_id}"')

    return db_gallery


def find_gallery_by_slug(brand_id: BrandID, slug: str) -> DbGallery | None:
    """Return the gallery of that brand and with that slug, if found."""
    return (
        db.session.scalars(
            select(DbGallery).filter_by(brand_id=brand_id).filter_by(slug=slug)
        )
        .unique()
        .one_or_none()
    )


def find_gallery_by_slug_with_images(
    brand_id: BrandID, slug: str
) -> DbGallery | None:
    """Return the gallery of that brand and with that slug, if found,
    with images.
    """
    return (
        db.session.scalars(
            select(DbGallery)
            .options(db.joinedload(DbGallery.images))
            .filter_by(brand_id=brand_id)
            .filter_by(slug=slug)
        )
        .unique()
        .one_or_none()
    )


def is_slug_available(brand_id: BrandID, slug: str) -> bool:
    """Check if the slug is yet unused."""
    return not db.session.scalar(
        select(
            db.exists()
            .where(DbGallery.brand_id == brand_id)
            .where(db.func.lower(DbGallery.slug) == slug.lower())
        )
    )


def get_galleries_for_brand(brand_id: BrandID) -> list[DbGallery]:
    """Return all galeries for the brand."""
    return (
        db.session.scalars(
            select(DbGallery)
            .filter_by(brand_id=brand_id)
            .order_by(DbGallery.position)
        )
        .unique()
        .all()
    )


def get_galleries_for_brand_with_images(brand_id: BrandID) -> list[DbGallery]:
    """Return all galeries for the brand, with images."""
    return (
        db.session.scalars(
            select(DbGallery)
            .options(db.joinedload(DbGallery.images))
            .filter(DbGallery.brand_id == brand_id)
            .order_by(DbGallery.position)
        )
        .unique()
        .all()
    )


# -------------------------------------------------------------------- #
# image


def create_image(image: GalleryImage) -> None:
    """Add an image to a gallery."""
    db_gallery = get_gallery(image.gallery_id)

    db_image = DbGalleryImage(
        image.id,
        image.created_at,
        image.gallery_id,
        image.filename_full,
        image.filename_preview,
        image.caption,
        image.hidden,
    )
    db_gallery.images.append(db_image)

    db.session.commit()
