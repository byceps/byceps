"""
byceps.services.ticketing.dbmodels.ticket_bundle
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship

from byceps.database import db
from byceps.services.party.models import PartyID
from byceps.services.ticketing.models.ticket import (
    TicketBundleID,
    TicketCategoryID,
)
from byceps.services.user.dbmodels.user import DbUser
from byceps.services.user.models.user import UserID
from byceps.util.instances import ReprBuilder
from byceps.util.uuid import generate_uuid7

from .category import DbTicketCategory


class DbTicketBundle(db.Model):
    """A set of tickets of the same category and with with a common
    owner, seat manager, and user manager, respectively.
    """

    __tablename__ = 'ticket_bundles'

    id: Mapped[TicketBundleID] = mapped_column(
        db.Uuid, default=generate_uuid7, primary_key=True
    )
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
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
    seats_managed_by_id: Mapped[
        Optional[UserID]  # noqa: F821, UP007
    ] = mapped_column(db.Uuid, db.ForeignKey('users.id'), index=True)
    seats_managed_by: Mapped[DbUser] = relationship(
        DbUser, foreign_keys=[seats_managed_by_id]
    )
    users_managed_by_id: Mapped[
        Optional[UserID]  # noqa: F821, UP007
    ] = mapped_column(db.Uuid, db.ForeignKey('users.id'), index=True)
    users_managed_by: Mapped[DbUser] = relationship(
        DbUser, foreign_keys=[users_managed_by_id]
    )
    label: Mapped[Optional[str]] = mapped_column(  # noqa: F821, UP007
        db.UnicodeText
    )
    revoked: Mapped[bool] = mapped_column(default=False)

    def __init__(
        self,
        party_id: PartyID,
        ticket_category_id: TicketCategoryID,
        ticket_quantity: int,
        owned_by_id: UserID,
        *,
        label: str | None = None,
    ) -> None:
        self.party_id = party_id
        self.ticket_category_id = ticket_category_id
        self.ticket_quantity = ticket_quantity
        self.owned_by_id = owned_by_id
        self.label = label

    def __repr__(self) -> str:
        return (
            ReprBuilder(self)
            .add('id', str(self.id))
            .add('party_id', self.party_id)
            .add('category', self.ticket_category.title)
            .add_with_lookup('ticket_quantity')
            .build()
        )
