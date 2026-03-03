"""
byceps.services.seating.dbmodels.seat
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import NamedTuple, TYPE_CHECKING

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

from .area import DbSeatingArea


class Point(NamedTuple):
    x: int
    y: int


class DbSeat(db.Model):
    """A seat."""

    __tablename__ = 'seats'

    id: Mapped[SeatID] = mapped_column(db.Uuid, primary_key=True)
    area_id: Mapped[SeatingAreaID] = mapped_column(
        db.Uuid, db.ForeignKey('seating_areas.id'), index=True
    )
    area: Mapped[DbSeatingArea] = relationship(backref='seats')
    coord_x: Mapped[int]
    coord_y: Mapped[int]
    rotation: Mapped[int | None]
    category_id: Mapped[TicketCategoryID] = mapped_column(
        db.Uuid,
        db.ForeignKey('ticket_categories.id'),
        index=True,
    )
    category: Mapped[DbTicketCategory] = relationship()
    label: Mapped[str | None] = mapped_column(db.UnicodeText)
    type_: Mapped[str | None] = mapped_column('type', db.UnicodeText)
    blocked: Mapped[bool]

    def __init__(
        self,
        seat_id: SeatID,
        area_id: SeatingAreaID,
        category_id: TicketCategoryID,
        *,
        coord_x: int = 0,
        coord_y: int = 0,
        rotation: int | None = None,
        label: str | None = None,
        type_: str | None = None,
        blocked: bool = False,
    ) -> None:
        self.id = seat_id
        self.area_id = area_id
        self.coord_x = coord_x
        self.coord_y = coord_y
        self.rotation = rotation
        self.category_id = category_id
        self.label = label
        self.type_ = type_
        self.blocked = blocked

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
