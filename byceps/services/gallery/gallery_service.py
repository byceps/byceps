"""
byceps.services.gallery.gallery_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from sqlalchemy import select

from byceps.database import db
from byceps.services.brand import brand_service
from byceps.services.brand.models import BrandID

from . import gallery_domain_service
from .dbmodels import DbGallery, DbGalleryImage
from .models import Gallery, GalleryID, GalleryImage, GalleryWithImages


# -------------------------------------------------------------------- #
# gallery


def create_gallery(
    brand_id: BrandID,
    slug: str,
    title: str,
    hidden: bool,
) -> Gallery:
    """Create a gallery."""
    db_brand = brand_service._get_db_brand(brand_id)
    if db_brand is None:
        raise ValueError(f'Unknown brand ID "{brand_id}"')

    gallery = gallery_domain_service.create_gallery(
        brand_id, slug, title, hidden
    )

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

    return gallery


def find_gallery(gallery_id: GalleryID) -> Gallery | None:
    """Return the gallery, if found."""
    db_gallery = _find_db_gallery(gallery_id)

    if db_gallery is None:
        return None

    return _db_entity_to_gallery(db_gallery)


def _find_db_gallery(gallery_id: GalleryID) -> DbGallery | None:
    return db.session.execute(
        select(DbGallery).filter_by(id=gallery_id)
    ).scalar_one_or_none()


def _get_db_gallery(gallery_id: GalleryID) -> DbGallery:
    db_gallery = _find_db_gallery(gallery_id)

    if db_gallery is None:
        raise ValueError(f'Unknown gallery ID "{gallery_id}"')

    return db_gallery


def find_gallery_by_slug_with_images(
    brand_id: BrandID, slug: str
) -> GalleryWithImages | None:
    """Return the gallery of that brand and with that slug, if found,
    with images.
    """
    db_gallery = (
        db.session.scalars(
            select(DbGallery)
            .options(db.joinedload(DbGallery.images))
            .filter_by(brand_id=brand_id)
            .filter_by(slug=slug)
        )
        .unique()
        .one_or_none()
    )

    if db_gallery is None:
        return None

    return _db_entity_to_gallery_with_images(db_gallery)


def is_slug_available(brand_id: BrandID, slug: str) -> bool:
    """Check if the slug is yet unused."""
    return not db.session.scalar(
        select(
            db.exists()
            .where(DbGallery.brand_id == brand_id)
            .where(db.func.lower(DbGallery.slug) == slug.lower())
        )
    )


def get_galleries_for_brand(brand_id: BrandID) -> list[Gallery]:
    """Return all galeries for the brand."""
    db_galleries = (
        db.session.scalars(select(DbGallery).filter_by(brand_id=brand_id))
        .unique()
        .all()
    )

    return [_db_entity_to_gallery(db_gallery) for db_gallery in db_galleries]


def get_galleries_for_brand_with_images(
    brand_id: BrandID,
) -> list[GalleryWithImages]:
    """Return all galeries for the brand, with images."""
    db_galleries = (
        db.session.scalars(
            select(DbGallery)
            .options(db.joinedload(DbGallery.images))
            .filter(DbGallery.brand_id == brand_id)
        )
        .unique()
        .all()
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
    db_gallery = _get_db_gallery(gallery.id)

    image = gallery_domain_service.create_image(
        gallery, filename_full, filename_preview, caption, hidden
    )

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

    return _db_entity_to_image(db_image, db_gallery)


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
