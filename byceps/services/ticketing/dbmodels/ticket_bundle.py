"""
byceps.services.ticketing.dbmodels.ticket_bundle
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from datetime import datetime

from byceps.database import db, generate_uuid7
from byceps.services.ticketing.models.ticket import TicketCategoryID
from byceps.services.user.dbmodels.user import DbUser
from byceps.typing import PartyID, UserID
from byceps.util.instances import ReprBuilder

from .category import DbTicketCategory


class DbTicketBundle(db.Model):
    """A set of tickets of the same category and with with a common
    owner, seat manager, and user manager, respectively.
    """

    __tablename__ = 'ticket_bundles'

    id = db.Column(db.Uuid, default=generate_uuid7, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    party_id = db.Column(
        db.UnicodeText, db.ForeignKey('parties.id'), index=True, nullable=False
    )
    ticket_category_id = db.Column(
        db.Uuid,
        db.ForeignKey('ticket_categories.id'),
        index=True,
        nullable=False,
    )
    ticket_category = db.relationship(DbTicketCategory)
    ticket_quantity = db.Column(db.Integer, nullable=False)
    owned_by_id = db.Column(
        db.Uuid, db.ForeignKey('users.id'), index=True, nullable=False
    )
    owned_by = db.relationship(DbUser, foreign_keys=[owned_by_id])
    seats_managed_by_id = db.Column(
        db.Uuid, db.ForeignKey('users.id'), index=True, nullable=True
    )
    seats_managed_by = db.relationship(
        DbUser, foreign_keys=[seats_managed_by_id]
    )
    users_managed_by_id = db.Column(
        db.Uuid, db.ForeignKey('users.id'), index=True, nullable=True
    )
    users_managed_by = db.relationship(
        DbUser, foreign_keys=[users_managed_by_id]
    )
    label = db.Column(db.UnicodeText, nullable=True)

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
