"""
byceps.services.party.dbmodels.party
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from typing import Optional

from ....database import db
from ....typing import BrandID, PartyID
from ....util.instances import ReprBuilder

from ...brand.dbmodels.brand import Brand


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
    ticket_management_enabled = db.Column(db.Boolean, default=False, nullable=False)
    seat_management_enabled = db.Column(db.Boolean, default=False, nullable=False)
    canceled = db.Column(db.Boolean, default=False, nullable=False)
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
    ) -> None:
        self.id = party_id
        self.brand_id = brand_id
        self.title = title
        self.starts_at = starts_at
        self.ends_at = ends_at
        self.max_ticket_quantity = max_ticket_quantity

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .build()
