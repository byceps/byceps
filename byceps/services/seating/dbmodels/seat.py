"""
byceps.services.seating.dbmodels.seat
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from typing import NamedTuple, Optional, TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship


if TYPE_CHECKING:
    hybrid_property = property
else:
    from sqlalchemy.ext.hybrid import hybrid_property

from byceps.database import db
from byceps.services.seating.models import SeatID, SeatingAreaID
from byceps.services.ticketing.dbmodels.category import DbTicketCategory
from byceps.services.ticketing.models.ticket import TicketCategoryID
from byceps.util.instances import ReprBuilder
from byceps.util.uuid import generate_uuid7

from .area import DbSeatingArea


class Point(NamedTuple):
    x: int
    y: int


class DbSeat(db.Model):
    """A seat."""

    __tablename__ = 'seats'

    id: Mapped[SeatID] = mapped_column(
        db.Uuid, default=generate_uuid7, primary_key=True
    )
    area_id: Mapped[SeatingAreaID] = mapped_column(
        db.Uuid, db.ForeignKey('seating_areas.id'), index=True
    )
    area: Mapped[DbSeatingArea] = relationship(DbSeatingArea, backref='seats')
    coord_x: Mapped[int]
    coord_y: Mapped[int]
    rotation: Mapped[Optional[int]]  # noqa: UP007
    category_id: Mapped[TicketCategoryID] = mapped_column(
        db.Uuid,
        db.ForeignKey('ticket_categories.id'),
        index=True,
    )
    category: Mapped[DbTicketCategory] = relationship(DbTicketCategory)
    label: Mapped[Optional[str]] = mapped_column(db.UnicodeText)  # noqa: UP007
    type_: Mapped[Optional[str]] = mapped_column(  # noqa: UP007
        'type', db.UnicodeText
    )

    def __init__(
        self,
        area_id: SeatingAreaID,
        category_id: TicketCategoryID,
        *,
        coord_x: int = 0,
        coord_y: int = 0,
        rotation: int | None = None,
        label: str | None = None,
        type_: str | None = None,
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
        return (
            ReprBuilder(self)
            .add('id', str(self.id))
            .add_with_lookup('area')
            .add_with_lookup('category')
            .add_with_lookup('label')
            .build()
        )
