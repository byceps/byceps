# -*- coding: utf-8 -*-

"""
byceps.services.seating.models.seat_group
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from sqlalchemy.ext.associationproxy import association_proxy

from ....database import db, generate_uuid
from ....util.instances import ReprBuilder

from .seat import Seat


class SeatGroup(db.Model):
    """A group of seats."""
    __tablename__ = 'seat_groups'
    __table_args__ = (
        db.UniqueConstraint('party_id', 'title'),
    )

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    party_id = db.Column(db.Unicode(20), db.ForeignKey('parties.id'), index=True, nullable=False)
    title = db.Column(db.Unicode(40), unique=True, nullable=False)

    seats = association_proxy('assignments', 'seat')

    def __init__(self, party_id, title):
        self.party_id = party_id
        self.title = title

    def __repr__(self):
        return ReprBuilder(self) \
            .add('id', str(self.id)) \
            .add('party', self.party_id) \
            .add_with_lookup('title') \
            .build()


class SeatGroupAssignment(db.Model):
    """The assignment of a seat to a seat group."""
    __tablename__ = 'seat_group_assignments'

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    group_id = db.Column(db.Uuid, db.ForeignKey('seat_groups.id'), index=True, nullable=False)
    group = db.relationship(SeatGroup, collection_class=set, backref='assignments')
    seat_id = db.Column(db.Uuid, db.ForeignKey('seats.id'), unique=True, index=True, nullable=False)
    seat = db.relationship(Seat)

    def __init__(self, group, seat_id):
        self.group = group
        self.seat_id = seat_id

    def __repr__(self):
        return ReprBuilder(self) \
            .add('id', str(self.id)) \
            .add('group', self.group.title) \
            .add_with_lookup('seat_id') \
            .build()
