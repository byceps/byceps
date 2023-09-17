"""
byceps.services.user_badge.dbmodels.badge
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column

from byceps.database import db, generate_uuid4
from byceps.services.user_badge.models import BadgeID
from byceps.typing import BrandID
from byceps.util.instances import ReprBuilder


class DbBadge(db.Model):
    """A global badge that can be awarded to a user."""

    __tablename__ = 'user_badges'

    id: Mapped[BadgeID] = mapped_column(
        db.Uuid, default=generate_uuid4, primary_key=True
    )
    slug: Mapped[str] = mapped_column(db.UnicodeText, unique=True, index=True)
    label: Mapped[str] = mapped_column(db.UnicodeText, unique=True)
    description: Mapped[str | None] = mapped_column(db.UnicodeText)
    image_filename: Mapped[str] = mapped_column(db.UnicodeText)
    brand_id: Mapped[str | None] = mapped_column(
        db.UnicodeText, db.ForeignKey('brands.id')
    )
    featured: Mapped[bool] = mapped_column(default=False)

    def __init__(
        self,
        slug: str,
        label: str,
        image_filename: str,
        *,
        description: str | None = None,
        brand_id: BrandID | None = None,
        featured: bool = False,
    ) -> None:
        self.slug = slug
        self.label = label
        self.description = description
        self.image_filename = image_filename
        self.brand_id = brand_id
        self.featured = featured

    def __repr__(self) -> str:
        return ReprBuilder(self).add_with_lookup('label').build()
