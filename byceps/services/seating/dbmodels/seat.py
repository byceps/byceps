"""
byceps.services.seating.dbmodels.seat
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections import namedtuple
from typing import Optional

from sqlalchemy.ext.hybrid import hybrid_property

from ....database import db, generate_uuid
from ....util.instances import ReprBuilder

from ...ticketing.dbmodels.category import Category
from ...ticketing.transfer.models import TicketCategoryID

from ..transfer.models import AreaID

from .area import Area


Point = namedtuple('Point', ['x', 'y'])


class Seat(db.Model):
    """A seat."""

    __tablename__ = 'seats'

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    area_id = db.Column(db.Uuid, db.ForeignKey('seating_areas.id'), index=True, nullable=False)
    area = db.relationship(Area, backref='seats')
    coord_x = db.Column(db.Integer, nullable=False)
    coord_y = db.Column(db.Integer, nullable=False)
    rotation = db.Column(db.SmallInteger, nullable=True)
    category_id = db.Column(db.Uuid, db.ForeignKey('ticket_categories.id'), index=True, nullable=False)
    category = db.relationship(Category)
    label = db.Column(db.UnicodeText, nullable=True)
    type_ = db.Column('type', db.UnicodeText, nullable=True)

    def __init__(
        self,
        area_id: AreaID,
        category_id: TicketCategoryID,
        *,
        coord_x: int = 0,
        coord_y: int = 0,
        rotation: Optional[int] = None,
        label: Optional[str] = None,
        type_: Optional[str] = None,
    ) -> None:
        self.area_id = area_id
        self.coord_x = coord_x
        self.coord_y = coord_y
        self.rotation = rotation
        self.category_id = category_id
        self.label = label
        self.type_ = type_

    @hybrid_property
    def coords(self) -> Point:
        return Point(x=self.coord_x, y=self.coord_y)

    @coords.setter
    def coords(self, point: Point) -> None:
        self.coord_x = point.x
        self.coord_y = point.y

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add('id', str(self.id)) \
            .add_with_lookup('area') \
            .add_with_lookup('category') \
            .add_with_lookup('label') \
            .build()
