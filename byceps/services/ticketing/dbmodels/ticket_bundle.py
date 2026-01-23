"""
byceps.services.ticketing.dbmodels.ticket_bundle
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship

from byceps.database import db
from byceps.services.party.models import PartyID
from byceps.services.ticketing.models.ticket import (
    TicketBundleID,
    TicketCategory,
    TicketCategoryID,
)
from byceps.services.user.dbmodels import DbUser
from byceps.services.user.models.user import UserID

from .category import DbTicketCategory


class DbTicketBundle(db.Model):
    """A set of tickets of the same category and with with a common
    owner, seat manager, and user manager, respectively.
    """

    __tablename__ = 'ticket_bundles'

    id: Mapped[TicketBundleID] = mapped_column(db.Uuid, primary_key=True)
    created_at: Mapped[datetime]
    party_id: Mapped[PartyID] = mapped_column(
        db.UnicodeText, db.ForeignKey('parties.id'), index=True
    )
    ticket_category_id: Mapped[TicketCategoryID] = mapped_column(
        db.Uuid,
        db.ForeignKey('ticket_categories.id'),
        index=True,
    )
    ticket_category: Mapped[DbTicketCategory] = relationship(DbTicketCategory)
    ticket_quantity: Mapped[int]
    owned_by_id: Mapped[UserID] = mapped_column(
        db.Uuid, db.ForeignKey('users.id'), index=True
    )
    owned_by: Mapped[DbUser] = relationship(DbUser, foreign_keys=[owned_by_id])
    seats_managed_by_id: Mapped[UserID | None] = mapped_column(
        db.Uuid, db.ForeignKey('users.id'), index=True
    )
    seats_managed_by: Mapped[DbUser] = relationship(
        DbUser, foreign_keys=[seats_managed_by_id]
    )
    users_managed_by_id: Mapped[UserID | None] = mapped_column(
        db.Uuid, db.ForeignKey('users.id'), index=True
    )
    users_managed_by: Mapped[DbUser] = relationship(
        DbUser, foreign_keys=[users_managed_by_id]
    )
    label: Mapped[str | None] = mapped_column(  # noqa: F821, UP007
        db.UnicodeText
    )
    revoked: Mapped[bool]

    def __init__(
        self,
        bundle_id: TicketBundleID,
        created_at: datetime,
        ticket_category: TicketCategory,
        ticket_quantity: int,
        owned_by_id: UserID,
        *,
        label: str | None = None,
        revoked: bool = False,
    ) -> None:
        self.id = bundle_id
        self.created_at = created_at
        self.party_id = ticket_category.party_id
        self.ticket_category_id = ticket_category.id
        self.ticket_quantity = ticket_quantity
        self.owned_by_id = owned_by_id
        self.label = label
        self.revoked = revoked
