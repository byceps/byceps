"""
byceps.services.ticketing.ticket_attendance_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections import Counter
from datetime import datetime
from itertools import chain
from typing import Optional, Sequence

from sqlalchemy import delete, select

from ...database import db, insert_ignore_on_conflict
from ...typing import BrandID, PartyID, UserID

from ..party import party_service
from ..party.dbmodels.party import DbParty
from ..party.models import Party

from .dbmodels.archived_attendance import DbArchivedAttendance
from .dbmodels.category import DbTicketCategory
from .dbmodels.ticket import DbTicket


def create_archived_attendance(user_id: UserID, party_id: PartyID) -> None:
    """Create an archived attendance of the user at the party."""
    table = DbArchivedAttendance.__table__

    values = {
        'user_id': str(user_id),
        'party_id': str(party_id),
    }

    insert_ignore_on_conflict(table, values)


def delete_archived_attendance(user_id: UserID, party_id: PartyID) -> None:
    """Delete the archived attendance of the user at the party."""
    db.session.execute(
        delete(DbArchivedAttendance).filter_by(
            user_id=user_id, party_id=party_id
        )
    )
    db.session.commit()


def get_attended_parties(
    user_id: UserID, limit_to_brand_id: Optional[BrandID] = None
) -> list[Party]:
    """Return the parties the user has attended in the past."""
    ticket_attendance_party_ids = _get_attended_party_ids(
        user_id, limit_to_brand_id
    )
    archived_attendance_party_ids = _get_archived_attendance_party_ids(
        user_id, limit_to_brand_id
    )

    party_ids = set(
        chain(ticket_attendance_party_ids, archived_attendance_party_ids)
    )

    return party_service.get_parties(party_ids)


def _get_attended_party_ids(
    user_id: UserID, limit_to_brand_id: Optional[BrandID] = None
) -> set[PartyID]:
    """Return the IDs of the non-legacy parties the user has attended."""
    stmt = (
        select(DbParty.id)
        .filter(DbParty.ends_at < datetime.utcnow())
        .filter(DbParty.canceled == False)  # noqa: E712
        .join(DbTicketCategory)
        .join(DbTicket)
        .filter(DbTicket.revoked == False)  # noqa: E712
        .filter(DbTicket.used_by_id == user_id)
    )

    if limit_to_brand_id is not None:
        stmt = stmt.filter(DbParty.brand_id == limit_to_brand_id)

    party_ids = db.session.scalars(stmt).all()

    return set(party_ids)


def _get_archived_attendance_party_ids(
    user_id: UserID, limit_to_brand_id: Optional[BrandID] = None
) -> set[PartyID]:
    """Return the IDs of the legacy parties the user has attended."""
    stmt = select(DbArchivedAttendance.party_id).filter(
        DbArchivedAttendance.user_id == user_id
    )

    if limit_to_brand_id is not None:
        stmt = stmt.join(DbParty).filter(DbParty.brand_id == limit_to_brand_id)

    party_ids = db.session.scalars(stmt).all()

    return set(party_ids)


def get_attendee_ids_for_party(party_id: PartyID) -> set[UserID]:
    """Return the party's attendees' IDs."""
    ticket_user_ids = db.session.scalars(
        select(DbTicket.used_by_id)
        .join(DbTicketCategory)
        .filter(DbTicketCategory.party_id == party_id)
        .filter(DbTicket.revoked == False)  # noqa: E712
        .filter(DbTicket.used_by_id.is_not(None))
    ).all()

    archived_attendance_user_ids = db.session.scalars(
        select(DbArchivedAttendance.user_id).filter(
            DbArchivedAttendance.party_id == party_id
        )
    ).all()

    return set(list(ticket_user_ids) + list(archived_attendance_user_ids))


def get_top_attendees_for_brand(brand_id: BrandID) -> list[tuple[UserID, int]]:
    """Return the attendees with the highest number of parties of this
    brand visited.
    """
    top_ticket_attendance_counts = _get_top_ticket_attendees_for_parties(
        brand_id
    )

    top_archived_attendance_counts = _get_top_archived_attendees_for_parties(
        brand_id
    )

    top_attendance_counts = _merge_top_attendance_counts(
        [top_ticket_attendance_counts, top_archived_attendance_counts]
    )

    # Select top attendees with more than one attendance.
    top_attendees = top_attendance_counts.most_common(50)
    top_attendees = [
        (user_id, attendance_count)
        for user_id, attendance_count in top_attendees
        if attendance_count > 1
    ]

    return top_attendees


def _get_top_ticket_attendees_for_parties(
    brand_id: BrandID,
) -> Sequence[tuple[UserID, int]]:
    user_id_column = db.aliased(DbTicket).used_by_id

    attendance_count = (
        select(
            db.func.count(DbTicketCategory.party_id.distinct()),
        )
        .join(DbParty)
        .filter(DbParty.brand_id == brand_id)
        .join(DbTicket)
        .filter(DbTicket.revoked == False)  # noqa: E712
        .filter(DbTicket.used_by_id == user_id_column)
        .scalar_subquery()
    )

    return (
        db.session.execute(
            select(
                user_id_column.distinct(),
                attendance_count,
            )
            .filter(user_id_column.is_not(None))
            .filter(attendance_count > 0)
            .order_by(attendance_count.desc())
        )
        .tuples()
        .all()
    )


def _get_top_archived_attendees_for_parties(
    brand_id: BrandID,
) -> Sequence[tuple[UserID, int]]:
    attendance_count_column = db.func.count(DbArchivedAttendance.user_id).label(
        'attendance_count'
    )

    return (
        db.session.execute(
            select(
                DbArchivedAttendance.user_id,
                attendance_count_column,
            )
            .join(DbParty)
            .filter(DbParty.brand_id == brand_id)
            .group_by(DbArchivedAttendance.user_id)
            .order_by(attendance_count_column.desc())
        )
        .tuples()
        .all()
    )


def _merge_top_attendance_counts(
    xs: list[Sequence[tuple[UserID, int]]]
) -> Counter[UserID]:
    counter: Counter = Counter()

    for x in xs:
        counter.update(dict(x))

    return counter
