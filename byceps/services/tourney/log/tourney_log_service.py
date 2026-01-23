"""
byceps.services.tourney.log.tourney_log_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.services.tourney.events import TourneyEvent
from byceps.services.tourney.models import Tourney
from byceps.services.user import user_service
from byceps.services.user.dbmodels import DbUser
from byceps.util.result import Err, Ok, Result

from . import tourney_log_repository, tourney_log_serialization_service
from .dbmodels import DbTourneyLogEntry
from .models import TourneyLogEntry


def persist_tourney_entry(entry: TourneyLogEntry) -> None:
    """Store a log entry for a tourney."""
    db_entry = to_tourney_db_entry(entry)

    tourney_log_repository.persist_tourney_entry(db_entry)


def to_tourney_db_entry(entry: TourneyLogEntry) -> DbTourneyLogEntry:
    """Convert tourney log entry to database entity."""
    return DbTourneyLogEntry(
        entry.id,
        entry.occurred_at,
        entry.event_type,
        entry.tourney.id,
        entry.initiator.id if entry.initiator else None,
        entry.data,
    )


def get_entries_for_tourney(tourney: Tourney) -> list[TourneyLogEntry]:
    """Return the log entries for that tourney."""
    db_entries_and_initiators = tourney_log_repository.get_entries_for_tourney(
        tourney.id
    )

    return [
        _db_entity_to_tourney_entry(db_entry, tourney, db_initiator)
        for db_entry, db_initiator in db_entries_and_initiators
    ]


def _db_entity_to_tourney_entry(
    db_entry: DbTourneyLogEntry, tourney: Tourney, db_initiator: DbUser
) -> TourneyLogEntry:
    return TourneyLogEntry(
        id=db_entry.id,
        occurred_at=db_entry.occurred_at,
        event_type=db_entry.event_type,
        tourney=tourney.to_basic_tourney(),
        initiator=user_service._db_entity_to_user(db_initiator),
        data=db_entry.data.copy(),
    )


def get_events_for_tourney(tourney: Tourney) -> Result[list[TourneyEvent], str]:
    """Return the events for that tourney."""
    entries = get_entries_for_tourney(tourney)

    events = []
    for entry in entries:
        match tourney_log_serialization_service.deserialize_tourney_event(
            entry
        ):
            case Ok(event):
                events.append(event)
            case Err(e):
                return Err(e)

    return Ok(events)
