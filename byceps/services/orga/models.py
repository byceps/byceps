"""
byceps.services.orga.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ...database import db
from ...typing import BrandID, UserID
from ...util.instances import ReprBuilder

from ..brand.models.brand import Brand
from ..user.models.user import User


class OrgaFlag(db.Model):
    """A user's organizer status for a single brand."""

    __tablename__ = 'orga_flags'

    brand_id = db.Column(db.UnicodeText, db.ForeignKey('brands.id'), primary_key=True)
    brand = db.relationship(Brand)
    user_id = db.Column(db.Uuid, db.ForeignKey('users.id'), primary_key=True)
    user = db.relationship(User)

    def __init__(self, brand_id: BrandID, user_id: UserID) -> None:
        self.brand_id = brand_id
        self.user_id = user_id

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add('brand', self.brand_id) \
            .add('user', self.user.screen_name) \
            .build()
