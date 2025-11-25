"""
byceps.services.tourney.log.tourney_log_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.services.tourney.models import Tourney
from byceps.services.user import user_service
from byceps.services.user.dbmodels.user import DbUser

from . import tourney_log_repository
from .dbmodels import DbTourneyLogEntry
from .models import TourneyLogEntry


def persist_entry(entry: TourneyLogEntry) -> None:
    """Store a log entry."""
    db_entry = to_db_entry(entry)

    tourney_log_repository.persist_entry(db_entry)


def to_db_entry(entry: TourneyLogEntry) -> DbTourneyLogEntry:
    """Convert log entry to database entity."""
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
        _db_entity_to_entry(db_entry, tourney, db_initiator)
        for db_entry, db_initiator in db_entries_and_initiators
    ]


def _db_entity_to_entry(
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
