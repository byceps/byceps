# -*- coding: utf-8 -*-

"""
byceps.blueprints.seating.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
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
        return self.filter_by(party_id=g.party.id)


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
    party_id = db.Column(db.Unicode(20), db.ForeignKey('parties.id'))
    party = db.relationship(Party, backref='seating_areas')
    slug = db.Column(db.Unicode(40))
    title = db.Column(db.Unicode(40))

    def __repr__(self):
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add_with_lookup('party') \
            .add_with_lookup('slug') \
            .add_with_lookup('title') \
            .build()


class Category(db.Model):
    """A seat's category which may (indirectly) indicate its price and
    features.
    """
    __tablename__ = 'seat_categories'
    __table_args__ = (
        db.UniqueConstraint('party_id', 'title'),
    )

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    party_id = db.Column(db.Unicode(20), db.ForeignKey('parties.id'))
    party = db.relationship(Party, backref='seat_categories')
    title = db.Column(db.Unicode(40))

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
    area_id = db.Column(db.Uuid, db.ForeignKey('seating_areas.id'))
    area = db.relationship(Area, backref='seats')
    coord_x = db.Column(db.Integer)
    coord_y = db.Column(db.Integer)
    category_id = db.Column(db.Uuid, db.ForeignKey('seat_categories.id'))
    category = db.relationship(Category, backref='seats')

    @hybrid_property
    def coords(self):
        return Point(x=self.coord_x, y=self.coord_y)

    @coords.setter
    def coords(self, point):
        self.coord_x = point.x
        self.coord_y = point.y

    def __repr__(self):
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add_with_lookup('area') \
            .add_with_lookup('coords') \
            .add_with_lookup('category') \
            .build()
