"""
byceps.services.orga.dbmodels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from sqlalchemy.orm import Mapped, mapped_column, relationship

from byceps.database import db
from byceps.services.brand.dbmodels.brand import DbBrand
from byceps.services.user.dbmodels.user import DbUser
from byceps.typing import BrandID, UserID
from byceps.util.instances import ReprBuilder


class DbOrgaFlag(db.Model):
    """A user's organizer status for a specific brand."""

    __tablename__ = 'orga_flags'

    user_id: Mapped[UserID] = mapped_column(
        db.Uuid, db.ForeignKey('users.id'), primary_key=True
    )
    user: Mapped[DbUser] = relationship(DbUser)
    brand_id: Mapped[BrandID] = mapped_column(
        db.UnicodeText, db.ForeignKey('brands.id'), primary_key=True
    )
    brand: Mapped[DbBrand] = relationship(DbBrand)

    def __init__(self, user_id: UserID, brand_id: BrandID) -> None:
        self.user_id = user_id
        self.brand_id = brand_id

    def __repr__(self) -> str:
        return (
            ReprBuilder(self)
            .add('user', self.user.screen_name)
            .add('brand', self.brand_id)
            .build()
        )
