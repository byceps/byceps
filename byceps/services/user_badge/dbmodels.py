"""
byceps.services.user_badge.dbmodels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column

from byceps.database import db
from byceps.services.brand.models import BrandID
from byceps.services.user.models.user import UserID
from byceps.services.user_badge.models import BadgeID
from byceps.util.instances import ReprBuilder
from byceps.util.uuid import generate_uuid4


class DbBadgeAwarding(db.Model):
    """The awarding of a badge to a user."""

    __tablename__ = 'user_badge_awardings'

    id: Mapped[UUID] = mapped_column(db.Uuid, primary_key=True)
    badge_id: Mapped[BadgeID] = mapped_column(
        db.Uuid, db.ForeignKey('user_badges.id')
    )
    awardee_id: Mapped[UserID] = mapped_column(
        db.Uuid, db.ForeignKey('users.id')
    )
    awarded_at: Mapped[datetime]

    def __init__(
        self,
        awarding_id: UUID,
        badge_id: BadgeID,
        awardee_id: UserID,
        awarded_at: datetime,
    ) -> None:
        self.id = awarding_id
        self.badge_id = badge_id
        self.awardee_id = awardee_id
        self.awarded_at = awarded_at


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
    brand_id: Mapped[BrandID | None] = mapped_column(
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
