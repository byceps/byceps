"""
byceps.services.seating.dbmodels.seat_group
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from uuid import UUID

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import Mapped, mapped_column, relationship

from byceps.database import db
from byceps.services.party.models import PartyID
from byceps.services.seating.models import SeatGroupID, SeatID
from byceps.services.ticketing.dbmodels.category import DbTicketCategory
from byceps.services.ticketing.dbmodels.ticket_bundle import DbTicketBundle
from byceps.services.ticketing.models.ticket import (
    TicketBundleID,
    TicketCategoryID,
)
from byceps.util.instances import ReprBuilder
from byceps.util.uuid import generate_uuid7

from .seat import DbSeat


class DbSeatGroup(db.Model):
    """A group of seats."""

    __tablename__ = 'seat_groups'
    __table_args__ = (db.UniqueConstraint('party_id', 'title'),)

    id: Mapped[SeatGroupID] = mapped_column(
        db.Uuid, default=generate_uuid7, primary_key=True
    )
    party_id: Mapped[PartyID] = mapped_column(
        db.UnicodeText, db.ForeignKey('parties.id'), index=True
    )
    ticket_category_id: Mapped[TicketCategoryID] = mapped_column(
        db.Uuid, db.ForeignKey('ticket_categories.id')
    )
    ticket_category: Mapped[DbTicketCategory] = relationship(DbTicketCategory)
    seat_quantity: Mapped[int] = mapped_column(db.Integer)
    title: Mapped[str] = mapped_column(db.UnicodeText)

    seats = association_proxy('assignments', 'seat')

    def __init__(
        self,
        party_id: PartyID,
        ticket_category_id: TicketCategoryID,
        seat_quantity: int,
        title: str,
    ) -> None:
        self.party_id = party_id
        self.ticket_category_id = ticket_category_id
        self.seat_quantity = seat_quantity
        self.title = title

    def __repr__(self) -> str:
        return (
            ReprBuilder(self)
            .add('id', str(self.id))
            .add('party', self.party_id)
            .add('ticket_category', self.ticket_category.title)
            .add_with_lookup('seat_quantity')
            .add_with_lookup('title')
            .build()
        )


class DbSeatGroupAssignment(db.Model):
    """The assignment of a seat to a seat group."""

    __tablename__ = 'seat_group_assignments'

    id: Mapped[UUID] = mapped_column(
        db.Uuid, default=generate_uuid7, primary_key=True
    )
    group_id: Mapped[SeatGroupID] = mapped_column(
        db.Uuid, db.ForeignKey('seat_groups.id'), index=True
    )
    group: Mapped[DbSeatGroup] = relationship(
        DbSeatGroup, collection_class=set, backref='assignments'
    )
    seat_id: Mapped[SeatID] = mapped_column(
        db.Uuid,
        db.ForeignKey('seats.id'),
        unique=True,
        index=True,
    )
    seat: Mapped[DbSeat] = relationship(
        DbSeat, backref=db.backref('assignment', uselist=False)
    )

    def __init__(self, group: DbSeatGroup, seat_id: SeatID) -> None:
        self.group = group
        self.seat_id = seat_id

    def __repr__(self) -> str:
        return (
            ReprBuilder(self)
            .add('id', str(self.id))
            .add('group', self.group.title)
            .add_with_lookup('seat_id')
            .build()
        )


class DbSeatGroupOccupancy(db.Model):
    """The occupancy of a seat group."""

    __tablename__ = 'seat_group_occupancies'

    id: Mapped[UUID] = mapped_column(
        db.Uuid, default=generate_uuid7, primary_key=True
    )
    seat_group_id: Mapped[SeatGroupID] = mapped_column(
        db.Uuid,
        db.ForeignKey('seat_groups.id'),
        unique=True,
        index=True,
    )
    seat_group: Mapped[DbSeatGroup] = relationship(
        DbSeatGroup, backref=db.backref('occupancy', uselist=False)
    )
    ticket_bundle_id: Mapped[TicketBundleID] = mapped_column(
        db.Uuid,
        db.ForeignKey('ticket_bundles.id'),
        unique=True,
        index=True,
    )
    ticket_bundle: Mapped[DbTicketBundle] = relationship(
        DbTicketBundle, backref=db.backref('occupied_seat_group', uselist=False)
    )

    def __init__(
        self, seat_group_id: SeatGroupID, ticket_bundle_id: TicketBundleID
    ) -> None:
        self.seat_group_id = seat_group_id
        self.ticket_bundle_id = ticket_bundle_id

    def __repr__(self) -> str:
        return (
            ReprBuilder(self)
            .add('seat_group_id', str(self.seat_group_id))
            .add('ticket_bundle_id', str(self.ticket_bundle_id))
            .build()
        )
