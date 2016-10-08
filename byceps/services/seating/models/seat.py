# -*- coding: utf-8 -*-

"""
byceps.services.seating.models.seat
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from collections import namedtuple

from sqlalchemy.ext.hybrid import hybrid_property

from ....database import db, generate_uuid
from ....util.instances import ReprBuilder

from .area import Area
from .category import Category


Point = namedtuple('Point', ['x', 'y'])


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
    label = db.Column(db.Unicode(40), nullable=True)

    def __init__(self, area, category, *, coord_x=0, coord_y=0):
        self.area = area
        self.coord_x = coord_x
        self.coord_y = coord_y
        self.category = category

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
            .add('id', str(self.id)) \
            .add_with_lookup('area') \
            .add_with_lookup('category') \
            .add_with_lookup('label') \
            .build()
