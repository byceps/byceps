"""
byceps.services.orga_presence.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from datetime import date, datetime
from itertools import groupby
from typing import Iterator, Sequence

import pendulum
from pendulum import DateTime

from ...database import db
from ...typing import PartyID
from ...util.datetime.range import create_adjacent_ranges, DateTimeRange
from ...util.datetime.timezone import get_timezone_string

from .dbmodels import Presence as DbPresence, Task as DbTask
from .transfer.models import PresenceTimeSlot, TaskTimeSlot, TimeSlot


def get_presences(party_id: PartyID) -> list[PresenceTimeSlot]:
    """Return all presences for that party."""
    presences = db.session \
        .query(DbPresence) \
        .filter_by(party_id=party_id) \
        .options(db.joinedload(DbPresence.orga)) \
        .all()

    return [_presence_to_time_slot(presence) for presence in presences]


def get_tasks(party_id: PartyID) -> list[TaskTimeSlot]:
    """Return all tasks for that party."""
    tasks = db.session \
        .query(DbTask) \
        .filter_by(party_id=party_id) \
        .all()

    return [_task_to_time_slot(task) for task in tasks]


def _presence_to_time_slot(presence: DbPresence) -> PresenceTimeSlot:
    return PresenceTimeSlot.from_(
        presence.orga,
        presence.starts_at,
        presence.ends_at,
    )


def _task_to_time_slot(task: DbTask) -> TaskTimeSlot:
    return TaskTimeSlot.from_(task.title, task.starts_at, task.ends_at)


# -------------------------------------------------------------------- #


def get_hour_ranges(time_slots: list[TimeSlot]) -> Iterator[DateTimeRange]:
    """Yield hour ranges based on the time slots."""
    time_slot_ranges = [time_slot.range for time_slot in time_slots]
    hour_starts = _get_hour_starts(time_slot_ranges)
    return create_adjacent_ranges(hour_starts)


def _get_hour_starts(dt_ranges: Sequence[DateTimeRange]) -> Iterator[datetime]:
    min_starts_at = _to_local_pendulum_datetime(_find_earliest_start(dt_ranges))
    max_ends_at = _to_local_pendulum_datetime(_find_latest_end(dt_ranges))

    period = pendulum.period(min_starts_at, max_ends_at)
    hour_starts = period.range('hours')

    return _to_datetimes_without_tzinfo(hour_starts)


def _find_earliest_start(dt_ranges: Sequence[DateTimeRange]) -> datetime:
    return min(dt_range.start for dt_range in dt_ranges)


def _find_latest_end(dt_ranges: Sequence[DateTimeRange]) -> datetime:
    return max(dt_range.end for dt_range in dt_ranges)


def _to_local_pendulum_datetime(dt: datetime) -> DateTime:
    return pendulum.instance(dt).in_tz(get_timezone_string())


def _to_datetimes_without_tzinfo(dts: Sequence[DateTime]) -> Iterator[datetime]:
    for dt in dts:
        yield dt.replace(tzinfo=None)


def get_days_and_hour_totals(
    hour_ranges: Sequence[DateTimeRange],
) -> Iterator[tuple[date, int]]:
    """Yield (day, relevant hours total) pairs."""

    def get_date(dt_range: DateTimeRange) -> date:
        return dt_range.start.date()

    for day, hour_ranges_for_day in groupby(hour_ranges, key=get_date):
        hour_total = len(list(hour_ranges_for_day))
        yield day, hour_total
