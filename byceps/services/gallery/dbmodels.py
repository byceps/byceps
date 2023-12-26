"""
byceps.services.gallery.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import backref, Mapped, mapped_column, relationship

from byceps.database import db
from byceps.services.brand.dbmodels import DbBrand
from byceps.services.brand.models import BrandID

from .models import GalleryID, GalleryImageID


class DbGallery(db.Model):
    """An image gallery."""

    __tablename__ = 'galleries'
    __table_args__ = (db.UniqueConstraint('brand_id', 'slug'),)

    id: Mapped[GalleryID] = mapped_column(db.Uuid, primary_key=True)
    created_at: Mapped[datetime]
    brand_id: Mapped[BrandID] = mapped_column(
        db.UnicodeText, db.ForeignKey('brands.id'), index=True
    )
    gallery = relationship(
        DbBrand,
        backref=backref(
            'galleries',
            order_by='DbGallery.position',
            collection_class=ordering_list('position', count_from=1),
        ),
    )
    position: Mapped[int]
    slug: Mapped[str] = mapped_column(db.UnicodeText)
    title: Mapped[str] = mapped_column(db.UnicodeText)
    hidden: Mapped[bool]

    title_image = association_proxy('title_image_association', 'image')

    def __init__(
        self,
        gallery_id: GalleryID,
        created_at: datetime,
        brand_id: BrandID,
        slug: str,
        title: str,
        hidden: bool,
    ) -> None:
        self.id = gallery_id
        self.created_at = created_at
        self.brand_id = brand_id
        self.slug = slug
        self.title = title
        self.hidden = hidden


class DbGalleryImage(db.Model):
    """An gallery image."""

    __tablename__ = 'gallery_images'

    id: Mapped[GalleryImageID] = mapped_column(db.Uuid, primary_key=True)
    created_at: Mapped[datetime]
    gallery_id: Mapped[GalleryID] = mapped_column(
        db.Uuid, db.ForeignKey('galleries.id'), index=True, nullable=False
    )
    gallery = relationship(
        DbGallery,
        backref=backref(
            'images',
            order_by='DbGalleryImage.position',
            collection_class=ordering_list('position', count_from=1),
        ),
    )
    position: Mapped[int]
    filename_full: Mapped[str] = mapped_column(db.UnicodeText)
    filename_preview: Mapped[str] = mapped_column(db.UnicodeText)
    caption: Mapped[str | None] = mapped_column(db.UnicodeText)
    hidden: Mapped[bool]

    def __init__(
        self,
        gallery_image_id: GalleryImageID,
        created_at: datetime,
        gallery_id: GalleryID,
        filename_full: str,
        filename_preview: str,
        caption: str | None,
        hidden: bool,
    ) -> None:
        self.id = gallery_image_id
        self.created_at = created_at
        self.gallery_id = gallery_id
        self.filename_full = filename_full
        self.filename_preview = filename_preview
        self.caption = caption
        self.hidden = hidden


class DbGalleryTitleImage(db.Model):
    """A title image for a gallery."""

    __tablename__ = 'gallery_title_images'

    gallery_id: Mapped[GalleryID] = mapped_column(
        db.Uuid, db.ForeignKey('galleries.id'), primary_key=True
    )
    gallery: Mapped[DbGallery] = relationship(
        DbGallery,
        backref=backref('title_image_association', uselist=False),
    )
    image_id: Mapped[GalleryImageID] = mapped_column(
        db.Uuid, db.ForeignKey('gallery_images.id'), unique=True
    )
    image: Mapped[DbGalleryImage] = relationship(DbGalleryImage)

    def __init__(self, gallery_id: GalleryID, image_id: GalleryImageID) -> None:
        self.gallery_id = gallery_id
        self.image_id = image_id
