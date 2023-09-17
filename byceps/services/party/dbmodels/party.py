"""
byceps.services.party.dbmodels.party
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship

from byceps.database import db
from byceps.services.brand.dbmodels.brand import DbBrand
from byceps.typing import BrandID, PartyID
from byceps.util.instances import ReprBuilder


class DbParty(db.Model):
    """A party."""

    __tablename__ = 'parties'

    id: Mapped[PartyID] = mapped_column(db.UnicodeText, primary_key=True)
    brand_id: Mapped[BrandID] = mapped_column(
        db.UnicodeText, db.ForeignKey('brands.id'), index=True
    )
    brand: Mapped[DbBrand] = relationship(DbBrand, backref='parties')
    title: Mapped[str] = mapped_column(db.UnicodeText, unique=True)
    starts_at: Mapped[datetime]
    ends_at: Mapped[datetime]
    max_ticket_quantity: Mapped[Optional[int]]  # noqa: UP007
    ticket_management_enabled: Mapped[bool]
    seat_management_enabled: Mapped[bool]
    canceled: Mapped[bool] = mapped_column(default=False)
    archived: Mapped[bool] = mapped_column(default=False)

    def __init__(
        self,
        party_id: PartyID,
        brand_id: BrandID,
        title: str,
        starts_at: datetime,
        ends_at: datetime,
        *,
        max_ticket_quantity: int | None = None,
        ticket_management_enabled: bool = False,
        seat_management_enabled: bool = False,
    ) -> None:
        self.id = party_id
        self.brand_id = brand_id
        self.title = title
        self.starts_at = starts_at
        self.ends_at = ends_at
        self.max_ticket_quantity = max_ticket_quantity
        self.ticket_management_enabled = ticket_management_enabled
        self.seat_management_enabled = seat_management_enabled

    def __repr__(self) -> str:
        return ReprBuilder(self).add_with_lookup('id').build()
