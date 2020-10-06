"""
byceps.services.ticketing.models.ticket_bundle
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from typing import Optional

from ....database import db, generate_uuid
from ....typing import UserID
from ....util.instances import ReprBuilder

from ...user.models.user import User

from ..transfer.models import TicketCategoryID

from .category import Category


class TicketBundle(db.Model):
    """A set of tickets of the same category and with with a common
    owner, seat manager, and user manager, respectively.
    """

    __tablename__ = 'ticket_bundles'

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ticket_category_id = db.Column(db.Uuid, db.ForeignKey('ticket_categories.id'), index=True, nullable=False)
    ticket_category = db.relationship(Category)
    ticket_quantity = db.Column(db.Integer, nullable=False)
    owned_by_id = db.Column(db.Uuid, db.ForeignKey('users.id'), index=True, nullable=False)
    owned_by = db.relationship(User, foreign_keys=[owned_by_id])
    seats_managed_by_id = db.Column(db.Uuid, db.ForeignKey('users.id'), index=True, nullable=True)
    seats_managed_by = db.relationship(User, foreign_keys=[seats_managed_by_id])
    users_managed_by_id = db.Column(db.Uuid, db.ForeignKey('users.id'), index=True, nullable=True)
    users_managed_by = db.relationship(User, foreign_keys=[users_managed_by_id])
    label = db.Column(db.UnicodeText, nullable=True)

    def __init__(
        self,
        ticket_category_id: TicketCategoryID,
        ticket_quantity: int,
        owned_by_id: UserID,
        *,
        label: Optional[str] = None,
    ) -> None:
        self.ticket_category_id = ticket_category_id
        self.ticket_quantity = ticket_quantity
        self.owned_by_id = owned_by_id
        self.label = label

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add('id', str(self.id)) \
            .add('party', self.ticket_category.party_id) \
            .add('category', self.ticket_category.title) \
            .add_with_lookup('ticket_quantity') \
            .build()
