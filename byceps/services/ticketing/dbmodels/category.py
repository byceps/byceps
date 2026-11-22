"""
byceps.services.ticketing.dbmodels.category
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.schema import ForeignKey, UniqueConstraint
from sqlalchemy.types import UnicodeText, Uuid

from byceps.database import db
from byceps.services.party.models import PartyID
from byceps.services.ticketing.models.ticket import TicketCategoryID


class DbTicketCategory(db.Model):
    """A ticket category."""

    __tablename__ = 'ticket_categories'
    __table_args__ = (UniqueConstraint('party_id', 'title'),)

    id: Mapped[TicketCategoryID] = mapped_column(Uuid, primary_key=True)
    party_id: Mapped[PartyID] = mapped_column(
        UnicodeText, ForeignKey('parties.id'), index=True
    )
    title: Mapped[str] = mapped_column(UnicodeText)

    def __init__(
        self, category_id: TicketCategoryID, party_id: PartyID, title: str
    ) -> None:
        self.id = category_id
        self.party_id = party_id
        self.title = title
