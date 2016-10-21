# -*- coding: utf-8 -*-

"""
byceps.services.seating.models.seat_group
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from enum import Enum

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property

from ....database import db, generate_uuid
from ....util.instances import ReprBuilder

from ...user.models.user import User

from .seat import Seat


State = Enum('State', ['available', 'reserved', 'occupied'])


class SeatGroup(db.Model):
    """A group of seats."""
    __tablename__ = 'seat_groups'
    __table_args__ = (
        db.UniqueConstraint('party_id', 'title'),
    )

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    party_id = db.Column(db.Unicode(20), db.ForeignKey('parties.id'), index=True, nullable=False)
    title = db.Column(db.Unicode(40), unique=True, nullable=False)
    _state = db.Column('state', db.Unicode(10), nullable=False)

    seats = association_proxy('assignments', 'seat')

    def __init__(self, party_id, title):
        self.party_id = party_id
        self.title = title
        self._state = State.available.name

    @hybrid_property
    def state(self):
        return State[self._state]

    @state.setter
    def state(self, state):
        assert state is not None
        self._state = state.name

    def __repr__(self):
        return ReprBuilder(self) \
            .add('id', str(self.id)) \
            .add('party', self.party_id) \
            .add_with_lookup('title') \
            .add('state', self.state.name) \
            .build()


class SeatGroupAssignment(db.Model):
    """The assignment of a seat to a seat group."""
    __tablename__ = 'seat_group_assignments'

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    group_id = db.Column(db.Uuid, db.ForeignKey('seat_groups.id'), index=True, nullable=False)
    group = db.relationship(SeatGroup, collection_class=set, backref='assignments')
    seat_id = db.Column(db.Uuid, db.ForeignKey('seats.id'), unique=True, index=True, nullable=False)
    seat = db.relationship(Seat)

    def __init__(self, group, seat):
        self.group = group
        self.seat = seat

    def __repr__(self):
        return ReprBuilder(self) \
            .add('id', str(self.id)) \
            .add('group', self.group.title) \
            .add_with_lookup('seat_id') \
            .build()


OccupancyState = Enum('OccupancyState', ['reserved', 'occupied'])


class Occupancy(db.Model):
    """The occupancy of a seat group."""
    __tablename__ = 'seat_group_occupancies'

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    seat_group_id = db.Column(db.Uuid, db.ForeignKey('seat_groups.id'), unique=True, index=True, nullable=False)
    seat_group = db.relationship(SeatGroup, backref=db.backref('occupancy', uselist=False))
    occupied_by_id = db.Column(db.Uuid, db.ForeignKey('users.id'), nullable=False)
    occupied_by = db.relationship(User)
    _state = db.Column('state', db.Unicode(10), nullable=False)

    def __init__(self, seat_group_id, occupied_by_id):
        self.seat_group_id = seat_group_id
        self.occupied_by_id = occupied_by_id
        self._state = OccupancyState.reserved.name

    @hybrid_property
    def state(self):
        return OccupancyState[self._state]

    @state.setter
    def state(self, state):
        assert state is not None
        self._state = state.name

    def __repr__(self):
        return ReprBuilder(self) \
            .add('seat_group_id', str(self.seat_group_id)) \
            .add('occupied_by', self.occupied_by.screen_name) \
            .add('state', self.state.name) \
            .build()
