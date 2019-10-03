"""
byceps.services.party.models.party
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from typing import Optional

from ....database import db
from ....typing import BrandID, PartyID
from ....util.instances import ReprBuilder

from ...brand.models.brand import Brand
from ...shop.shop.transfer.models import ShopID


class Party(db.Model):
    """A party."""
    __tablename__ = 'parties'

    id = db.Column(db.UnicodeText, primary_key=True)
    brand_id = db.Column(db.UnicodeText, db.ForeignKey('brands.id'), index=True, nullable=False)
    brand = db.relationship(Brand, backref='parties')
    title = db.Column(db.UnicodeText, unique=True, nullable=False)
    starts_at = db.Column(db.DateTime, nullable=False)
    ends_at = db.Column(db.DateTime, nullable=False)
    max_ticket_quantity = db.Column(db.Integer, nullable=True)
    shop_id = db.Column(db.UnicodeText, db.ForeignKey('shops.id'), index=True, nullable=True)
    archived = db.Column(db.Boolean, default=False, nullable=False)

    def __init__(
        self,
        party_id: PartyID,
        brand_id: BrandID,
        title: str,
        starts_at: datetime,
        ends_at: datetime,
        *,
        max_ticket_quantity: Optional[int] = None,
        shop_id: Optional[ShopID] = None,
    ) -> None:
        self.id = party_id
        self.brand_id = brand_id
        self.title = title
        self.starts_at = starts_at
        self.ends_at = ends_at
        self.max_ticket_quantity = max_ticket_quantity
        self.shop_id = shop_id

    @property
    def is_over(self) -> bool:
        """Returns true if the party has ended."""
        return self.ends_at < datetime.utcnow()

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .build()
