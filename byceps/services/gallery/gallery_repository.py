"""
byceps.services.gallery.gallery_repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Sequence

from sqlalchemy import delete, select

from byceps.database import db, upsert
from byceps.services.brand import brand_service
from byceps.services.brand.models import BrandID
from byceps.util.result import Err, Ok, Result

from .dbmodels import DbGallery, DbGalleryImage, DbGalleryTitleImage
from .errors import GalleryAlreadyAtBottomError, GalleryAlreadyAtTopError
from .models import Gallery, GalleryID, GalleryImage, GalleryImageID


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


def move_gallery_up(
    gallery_id: GalleryID,
) -> Result[None, GalleryAlreadyAtTopError]:
    """Move a gallery upwards by one position."""
    db_gallery = get_gallery(gallery_id)

    db_gallery_list = db_gallery.brand.galleries

    if db_gallery.position == 1:
        return Err(GalleryAlreadyAtTopError())

    db_popped_category = db_gallery_list.pop(db_gallery.position - 1)
    db_gallery_list.insert(db_popped_category.position - 2, db_popped_category)

    db.session.commit()

    return Ok(None)


def move_gallery_down(
    gallery_id: GalleryID,
) -> Result[None, GalleryAlreadyAtBottomError]:
    """Move a gallery downwards by one position."""
    db_gallery = get_gallery(gallery_id)

    db_gallery_list = db_gallery.brand.galleries

    if db_gallery.position == len(db_gallery_list):
        return Err(GalleryAlreadyAtBottomError())

    db_popped_category = db_gallery_list.pop(db_gallery.position - 1)
    db_gallery_list.insert(db_popped_category.position, db_popped_category)

    db.session.commit()

    return Ok(None)


def set_gallery_title_image(
    gallery_id: GalleryID, image_id: GalleryImageID
) -> None:
    """Set a title image for the gallery."""
    table = DbGalleryTitleImage.__table__
    identifier = {'gallery_id': gallery_id}
    replacement = {'image_id': image_id}

    upsert(table, identifier, replacement)


def remove_gallery_title_image(gallery_id: GalleryID) -> None:
    """Remove the title image for the gallery."""
    db.session.execute(
        delete(DbGalleryTitleImage).filter_by(gallery_id=gallery_id)
    )
    db.session.commit()


def delete_gallery(gallery_id: GalleryID) -> None:
    """Delete a gallery and its associated image records, but not the
    image files.
    """
    db.session.execute(
        delete(DbGalleryTitleImage).filter_by(gallery_id=gallery_id)
    )
    db.session.execute(delete(DbGalleryImage).filter_by(gallery_id=gallery_id))
    db.session.execute(delete(DbGallery).filter_by(id=gallery_id))
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


def get_galleries_for_brand(brand_id: BrandID) -> Sequence[DbGallery]:
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


def get_galleries_for_brand_with_images(
    brand_id: BrandID,
) -> Sequence[DbGallery]:
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
