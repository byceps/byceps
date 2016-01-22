# -*- coding: utf-8 -*-

"""
byceps.blueprints.ticket.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime

from ...database import BaseQuery, db, generate_uuid
from ...util.instances import ReprBuilder

from ..party.models import Party
from ..seating.models import Category, Seat
from ..user.models import User


class TicketQuery(BaseQuery):

    def for_party(self, party):
        return self.join(Category).filter(Category.party_id == party.id)


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
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    category_id = db.Column(db.Uuid, db.ForeignKey('seat_categories.id'), index=True, nullable=False)
    category = db.relationship(Category)
    owned_by_id = db.Column(db.Uuid, db.ForeignKey('users.id'), index=True, nullable=False)
    owned_by = db.relationship(User, foreign_keys=[owned_by_id])
    seat_managed_by_id = db.Column(db.Uuid, db.ForeignKey('users.id'), index=True, nullable=True)
    seat_managed_by = db.relationship(User, foreign_keys=[seat_managed_by_id])
    user_managed_by_id = db.Column(db.Uuid, db.ForeignKey('users.id'), index=True, nullable=True)
    user_managed_by = db.relationship(User, foreign_keys=[user_managed_by_id])
    occupied_seat_id = db.Column(db.Uuid, db.ForeignKey('seats.id'), index=True, nullable=True, unique=True)
    occupied_seat = db.relationship(Seat, backref=db.backref('occupied_by_ticket', uselist=False))
    used_by_id = db.Column(db.Uuid, db.ForeignKey('users.id'), index=True, nullable=True)
    used_by = db.relationship(User, foreign_keys=[used_by_id])

    def __init__(self, category, owned_by):
        self.category = category
        self.owned_by = owned_by

    @property
    def party(self):
        """Return the party this ticket belongs to."""
        return self.category.party

    def get_seat_manager(self):
        """Return the user that may choose the seat for this ticket."""
        return self.seat_managed_by or self.owned_by

    def get_user_manager(self):
        """Return the user that may choose the user of this ticket."""
        return self.user_managed_by or self.owned_by

    def is_managed_by(self, user):
        """Return `True` if the user may choose the seat for or the
        user of this ticket.
        """
        return self.is_seat_managed_by(user) or self.is_user_managed_by(user)

    def is_seat_managed_by(self, user):
        """Return `True` if the user may choose the seat for this ticket."""
        if user is None:
            return False

        return ((self.seat_managed_by is None) and (self.owned_by == user)) or \
            (self.seat_managed_by == user)

    def is_user_managed_by(self, user):
        """Return `True` if the user may choose the user of this ticket."""
        if user is None:
            return False

        return ((self.user_managed_by is None) and (self.owned_by == user)) or \
            (self.user_managed_by == user)

    def __repr__(self):
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add_with_lookup('category') \
            .add_with_lookup('owned_by') \
            .add_with_lookup('occupied_seat') \
            .add_with_lookup('used_by') \
            .build()
