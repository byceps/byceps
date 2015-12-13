# -*- coding: utf-8 -*-

"""
byceps.blueprints.seating.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from collections import namedtuple

from flask import g
from sqlalchemy.ext.hybrid import hybrid_property

from ...database import BaseQuery, db, generate_uuid
from ...util.instances import ReprBuilder

from ..party.models import Party


Point = namedtuple('Point', ['x', 'y'])


class AreaQuery(BaseQuery):

    def for_current_party(self):
        return self.for_party(g.party)

    def for_party(self, party):
        return self.filter_by(party_id=party.id)


class Area(db.Model):
    """A spatial representation of seats in one part of the party
    location.

    Seats can belong to different categories.
    """
    __tablename__ = 'seating_areas'
    __table_args__ = (
        db.UniqueConstraint('party_id', 'slug'),
        db.UniqueConstraint('party_id', 'title'),
    )
    query_class = AreaQuery

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    party_id = db.Column(db.Unicode(20), db.ForeignKey('parties.id'), index=True, nullable=False)
    party = db.relationship(Party, backref='seating_areas')
    slug = db.Column(db.Unicode(40), nullable=False)
    title = db.Column(db.Unicode(40), nullable=False)
    image_filename = db.Column(db.Unicode(40), nullable=True)
    image_width = db.Column(db.Integer, nullable=True)
    image_height = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add_with_lookup('party') \
            .add_with_lookup('slug') \
            .build()


class CategoryQuery(BaseQuery):

    def for_party(self, party):
        return self.filter_by(party_id=party.id)


class Category(db.Model):
    """A seat's category which may (indirectly) indicate its price and
    features.
    """
    __tablename__ = 'seat_categories'
    __table_args__ = (
        db.UniqueConstraint('party_id', 'title'),
    )
    query_class = CategoryQuery

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    party_id = db.Column(db.Unicode(20), db.ForeignKey('parties.id'), index=True, nullable=False)
    party = db.relationship(Party, backref='seat_categories')
    title = db.Column(db.Unicode(40), nullable=False)

    def __repr__(self):
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add_with_lookup('party') \
            .add_with_lookup('title') \
            .build()


class Seat(db.Model):
    """A seat."""
    __tablename__ = 'seats'

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    area_id = db.Column(db.Uuid, db.ForeignKey('seating_areas.id'), index=True, nullable=False)
    area = db.relationship(Area, backref='seats')
    coord_x = db.Column(db.Integer, nullable=False)
    coord_y = db.Column(db.Integer, nullable=False)
    category_id = db.Column(db.Uuid, db.ForeignKey('seat_categories.id'), index=True, nullable=False)
    category = db.relationship(Category, backref='seats')

    @hybrid_property
    def coords(self):
        return Point(x=self.coord_x, y=self.coord_y)

    @coords.setter
    def coords(self, point):
        self.coord_x = point.x
        self.coord_y = point.y

    @property
    def is_occupied(self):
        """Return `True` if the seat is occupied by a ticket."""
        return bool(self.occupied_by_ticket)

    @property
    def has_user(self):
        """Return `True` if the seat is occupied by a ticket, and that
        ticket is assigned to a user.
        """
        return self.is_occupied and bool(self.occupied_by_ticket.used_by)

    @property
    def user(self):
        """Return the user to which the ticket that occupies this seat
        is assigned, or `None` if this seat is not occupied by a ticket
        or the ticket is not assigned to a user.
        """
        if self.has_user:
            return self.occupied_by_ticket.used_by

    def __repr__(self):
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add_with_lookup('area') \
            .add_with_lookup('category') \
            .build()
