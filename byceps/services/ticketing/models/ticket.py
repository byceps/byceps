"""
byceps.services.ticketing.models.ticket
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from typing import Optional

from ....database import BaseQuery, db, generate_uuid
from ....typing import PartyID, UserID
from ....util.instances import ReprBuilder

from ...seating.models.seat import Seat
from ...shop.order.transfer.models import OrderNumber
from ...user.models.user import User

from ..transfer.models import TicketCategoryID, TicketCode

from .category import Category
from .ticket_bundle import TicketBundle


class TicketQuery(BaseQuery):

    def for_party(self, party_id: PartyID) -> BaseQuery:
        return self.join(Category).filter(Category.party_id == party_id)


class Ticket(db.Model):
    """A ticket that permits to attend a party and to occupy a seat.

    A user can generally occupy multiple seats which is why no database
    constraints are in place to prevent that. However, if it makes sense
    for a party or party series, a user can be limited to occupy only a
    single seat by introducing custom guard code that blocks further
    attempts to reserve a seat.
    """
    __tablename__ = 'tickets'
    query_class = TicketQuery

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    code = db.Column(db.UnicodeText, unique=True, index=True, nullable=False)
    bundle_id = db.Column(db.Uuid, db.ForeignKey('ticket_bundles.id'), index=True, nullable=True)
    bundle = db.relationship(TicketBundle, backref='tickets')
    category_id = db.Column(db.Uuid, db.ForeignKey('ticket_categories.id'), index=True, nullable=False)
    category = db.relationship(Category)
    owned_by_id = db.Column(db.Uuid, db.ForeignKey('users.id'), index=True, nullable=False)
    owned_by = db.relationship(User, foreign_keys=[owned_by_id])
    order_number = db.Column(db.UnicodeText, db.ForeignKey('shop_orders.order_number'), index=True, nullable=True)
    seat_managed_by_id = db.Column(db.Uuid, db.ForeignKey('users.id'), index=True, nullable=True)
    seat_managed_by = db.relationship(User, foreign_keys=[seat_managed_by_id])
    user_managed_by_id = db.Column(db.Uuid, db.ForeignKey('users.id'), index=True, nullable=True)
    user_managed_by = db.relationship(User, foreign_keys=[user_managed_by_id])
    occupied_seat_id = db.Column(db.Uuid, db.ForeignKey('seats.id'), index=True, nullable=True, unique=True)
    occupied_seat = db.relationship(Seat, backref=db.backref('occupied_by_ticket', uselist=False))
    used_by_id = db.Column(db.Uuid, db.ForeignKey('users.id'), index=True, nullable=True)
    used_by = db.relationship(User, foreign_keys=[used_by_id])
    revoked = db.Column(db.Boolean, default=False, nullable=False)
    user_checked_in = db.Column(db.Boolean, default=False, nullable=False)

    def __init__(
        self,
        code: TicketCode,
        category_id: TicketCategoryID,
        owned_by_id: UserID,
        *,
        bundle: Optional[TicketBundle] = None,
        order_number: Optional[OrderNumber] = None,
    ) -> None:
        self.code = code
        self.bundle = bundle
        self.category_id = category_id
        self.owned_by_id = owned_by_id
        self.order_number = order_number

    @property
    def belongs_to_bundle(self) -> bool:
        """Return `True` if this ticket is part of a ticket bundle, or
        `False` if it is stand-alone.
        """
        return self.bundle_id is not None

    def is_owned_by(self, user_id: UserID):
        """Return `True` if the user owns this ticket."""
        return self.owned_by_id == user_id

    def get_seat_manager(self) -> User:
        """Return the user that may choose the seat for this ticket."""
        return self.seat_managed_by or self.owned_by

    def get_user_manager(self) -> User:
        """Return the user that may choose the user of this ticket."""
        return self.user_managed_by or self.owned_by

    def is_managed_by(self, user_id: UserID) -> bool:
        """Return `True` if the user may choose the seat for or the
        user of this ticket.
        """
        return self.is_seat_managed_by(user_id) \
            or self.is_user_managed_by(user_id)

    def is_seat_managed_by(self, user_id: UserID) -> bool:
        """Return `True` if the user may choose the seat for this ticket."""
        return ((self.seat_managed_by_id is None) and self.is_owned_by(user_id)) or \
            (self.seat_managed_by_id == user_id)

    def is_user_managed_by(self, user_id: UserID) -> bool:
        """Return `True` if the user may choose the user of this ticket."""
        return ((self.user_managed_by_id is None) and self.is_owned_by(user_id)) or \
            (self.user_managed_by_id == user_id)

    def __repr__(self) -> str:
        def user(user: User) -> Optional[str]:
            return user.screen_name if (user is not None) else None

        def occupied_seat() -> Optional[str]:
            seat = self.occupied_seat

            if seat is None:
                return None

            return '{{area={!r}, label={!r}}}' \
                .format(seat.area.title, seat.label)

        return ReprBuilder(self) \
            .add('id', str(self.id)) \
            .add('party', self.category.party_id) \
            .add('category', self.category.title) \
            .add('owned_by', user(self.owned_by)) \
            .add_custom('occupied_seat={}'.format(occupied_seat())) \
            .add('used_by', user(self.used_by)) \
            .build()
