"""
byceps.services.orga_presence.orga_presence_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import date, datetime, timedelta, timezone
from itertools import groupby
from typing import Iterable, Iterator
from uuid import UUID
from zoneinfo import ZoneInfo

from flask import current_app
from sqlalchemy import delete

from ...database import db
from ...typing import PartyID, UserID
from ...util.datetime.range import create_adjacent_ranges, DateTimeRange

from ..party import party_service

from .dbmodels import DbPresence, DbTask, DbTimeSlot
from .models import PresenceTimeSlot, TaskTimeSlot, TimeSlot


def create_presence(
    party_id: PartyID, orga_id: UserID, starts_at: datetime, ends_at: datetime
) -> PresenceTimeSlot:
    """Create a presence for the orga during the party."""
    party = party_service.get_party(party_id)

    presence = DbPresence(
        party_id=party.id, starts_at=starts_at, ends_at=ends_at, orga_id=orga_id
    )
    db.session.add(presence)
    db.session.commit()

    return _presence_to_time_slot(presence)


def delete_time_slot(time_slot_id: UUID) -> None:
    """Delete a time slot."""
    db.session.execute(
        delete(DbTimeSlot)
        .where(DbTimeSlot.id == time_slot_id)
        .execution_options(synchronize_session='fetch')
    )
    db.session.commit()


def get_presences(party_id: PartyID) -> list[PresenceTimeSlot]:
    """Return all presences for that party."""
    presences = (
        db.session.query(DbPresence)
        .filter_by(party_id=party_id)
        .options(db.joinedload(DbPresence.orga))
        .all()
    )

    return [_presence_to_time_slot(presence) for presence in presences]


def get_tasks(party_id: PartyID) -> list[TaskTimeSlot]:
    """Return all tasks for that party."""
    tasks = db.session.query(DbTask).filter_by(party_id=party_id).all()

    return [_task_to_time_slot(task) for task in tasks]


def _presence_to_time_slot(presence: DbPresence) -> PresenceTimeSlot:
    return PresenceTimeSlot.from_(
        presence.id,
        presence.orga,
        presence.starts_at,
        presence.ends_at,
    )


def _task_to_time_slot(task: DbTask) -> TaskTimeSlot:
    return TaskTimeSlot.from_(
        task.id,
        task.title,
        task.starts_at,
        task.ends_at,
    )


# -------------------------------------------------------------------- #


def get_hour_ranges(time_slots: list[TimeSlot]) -> Iterator[DateTimeRange]:
    """Yield hour ranges based on the time slots."""
    time_slot_ranges = [time_slot.range for time_slot in time_slots]
    hour_starts = _get_hour_starts(time_slot_ranges)
    return create_adjacent_ranges(hour_starts)


def _get_hour_starts(dt_ranges: Iterable[DateTimeRange]) -> Iterator[datetime]:
    min_starts_at_utc = _find_earliest_start(dt_ranges)
    max_ends_at_utc = _find_latest_end(dt_ranges)

    # Generate full hours.
    min_starts_at_utc = min_starts_at_utc.replace(
        minute=0, second=0, microsecond=0
    )

    min_starts_at_utc = min_starts_at_utc.replace(tzinfo=timezone.utc)
    max_ends_at_utc = max_ends_at_utc.replace(tzinfo=timezone.utc)

    local_tz = ZoneInfo(current_app.config['TIMEZONE'])
    min_starts_at_local = min_starts_at_utc.astimezone(local_tz)
    max_ends_at_local = max_ends_at_utc.astimezone(local_tz)

    hour_starts = _generate_hour_starts(min_starts_at_local, max_ends_at_local)

    # Remove timezone info for comparability with naive datetimes.
    return (dt.replace(tzinfo=None) for dt in hour_starts)


def _find_earliest_start(dt_ranges: Iterable[DateTimeRange]) -> datetime:
    return min(dt_range.start for dt_range in dt_ranges)


def _find_latest_end(dt_ranges: Iterable[DateTimeRange]) -> datetime:
    return max(dt_range.end for dt_range in dt_ranges)


def _generate_hour_starts(start: datetime, end: datetime) -> Iterator[datetime]:
    one_hour = timedelta(hours=1)
    x = start
    while x <= end:
        yield x
        x += one_hour


def get_days_and_hour_totals(
    hour_ranges: Iterable[DateTimeRange],
) -> Iterator[tuple[date, int]]:
    """Yield (day, relevant hours total) pairs."""

    def get_date(dt_range: DateTimeRange) -> date:
        return dt_range.start.date()

    for day, hour_ranges_for_day in groupby(hour_ranges, key=get_date):
        hour_total = len(list(hour_ranges_for_day))
        yield day, hour_total
