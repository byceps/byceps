"""
byceps.services.ticketing.attendance_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from collections import defaultdict
from datetime import datetime
from itertools import chain
from typing import Dict, List, Set

from ...database import db
from ...typing import PartyID, UserID

from ..party.models.party import Party as DbParty
from ..party import service as party_service
from ..party.transfer.models import Party
from ..user import service as user_service
from ..user.transfer.models import User

from .models.archived_attendance import (
    ArchivedAttendance as DbArchivedAttendance,
)
from .models.category import Category as DbCategory
from .models.ticket import Ticket as DbTicket


def create_archived_attendance(
    user_id: UserID, party_id: PartyID
) -> DbArchivedAttendance:
    """Create an archived attendance of the user at the party."""
    attendance = DbArchivedAttendance(user_id, party_id)

    db.session.add(attendance)
    db.session.commit()

    return attendance


def get_attended_parties(user_id: UserID) -> List[Party]:
    """Return the parties the user has attended in the past."""
    ticket_attendance_party_ids = _get_attended_party_ids(user_id)
    archived_attendance_party_ids = _get_archived_attendance_party_ids(user_id)

    party_ids = set(chain(ticket_attendance_party_ids,
                          archived_attendance_party_ids))

    return party_service.get_parties(party_ids)


def _get_attended_party_ids(user_id: UserID) -> Set[PartyID]:
    """Return the IDs of the non-legacy parties the user has attended."""
    party_id_rows = db.session \
        .query(DbParty.id) \
        .filter(DbParty.ends_at < datetime.utcnow()) \
        .join(DbCategory) \
        .join(DbTicket) \
        .filter(DbTicket.used_by_id == user_id) \
        .all()

    return {row[0] for row in party_id_rows}


def _get_archived_attendance_party_ids(user_id: UserID) -> Set[PartyID]:
    """Return the IDs of the legacy parties the user has attended."""
    party_id_rows = db.session \
        .query(DbArchivedAttendance.party_id) \
        .filter(DbArchivedAttendance.user_id == user_id) \
        .all()

    return {row[0] for row in party_id_rows}


def get_attendees_by_party(party_ids: Set[PartyID]) -> Dict[PartyID, Set[User]]:
    """Return the parties' attendees, indexed by party."""
    if not party_ids:
        return {}

    attendee_ids_by_party_id = get_attendee_ids_for_parties(party_ids)

    all_attendee_ids = set(
        chain.from_iterable(attendee_ids_by_party_id.values()))
    all_attendees = user_service.find_users(all_attendee_ids,
                                            include_avatars=True)
    all_attendees_by_id = user_service.index_users_by_id(all_attendees)

    attendees_by_party_id = {}
    for party_id in party_ids:
        attendee_ids = attendee_ids_by_party_id.get(party_id, set())

        attendees = {all_attendees_by_id[attendee_id]
                     for attendee_id in attendee_ids}

        attendees_by_party_id[party_id] = attendees

    return attendees_by_party_id


def get_attendee_ids_for_parties(
    party_ids: Set[PartyID]
) -> Dict[PartyID, Set[UserID]]:
    """Return the partys' attendee IDs, indexed by party ID."""
    if not party_ids:
        return {}

    ticket_rows = db.session \
        .query(DbCategory.party_id, DbTicket.used_by_id) \
        .filter(DbCategory.party_id.in_(party_ids)) \
        .join(DbTicket) \
        .filter(DbTicket.used_by_id != None) \
        .all()

    archived_attendance_rows = db.session \
        .query(
            DbArchivedAttendance.party_id,
            DbArchivedAttendance.user_id
        ) \
        .filter(DbArchivedAttendance.party_id.in_(party_ids)) \
        .all()

    rows = ticket_rows + archived_attendance_rows

    attendee_ids_by_party_id: Dict[PartyID, Set[UserID]] = defaultdict(set)
    for party_id, attendee_id in rows:
        attendee_ids_by_party_id[party_id].add(attendee_id)

    return dict(attendee_ids_by_party_id)
