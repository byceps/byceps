"""
byceps.services.tourney.log.tourney_log_domain_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from byceps.services.tourney.models import MatchID, ParticipantID, Tourney
from byceps.services.user.models.user import User
from byceps.util.uuid import generate_uuid7

from .models import (
    LogEntryData,
    TourneyLogEntry,
    TourneyMatchLogEntry,
    TourneyParticipantLogEntry,
)


def build_tourney_entry(
    event_type: str,
    tourney: Tourney,
    data: LogEntryData,
    *,
    occurred_at: datetime | None = None,
    initiator: User | None = None,
) -> TourneyLogEntry:
    """Assemble a tourney log entry."""
    entry_id = generate_uuid7()

    if occurred_at is None:
        occurred_at = datetime.utcnow()

    return TourneyLogEntry(
        id=entry_id,
        occurred_at=occurred_at,
        event_type=event_type,
        tourney=tourney.to_basic_tourney(),
        initiator=initiator,
        data=data,
    )


def build_participant_entry(
    event_type: str,
    participant_id: ParticipantID,
    data: LogEntryData,
    *,
    occurred_at: datetime | None = None,
    initiator: User | None = None,
) -> TourneyParticipantLogEntry:
    """Assemble a tourney participant log entry."""
    entry_id = generate_uuid7()

    if occurred_at is None:
        occurred_at = datetime.utcnow()

    return TourneyParticipantLogEntry(
        id=entry_id,
        occurred_at=occurred_at,
        event_type=event_type,
        participant_id=participant_id,
        initiator=initiator,
        data=data,
    )


def build_match_entry(
    event_type: str,
    match_id: MatchID,
    data: LogEntryData,
    *,
    occurred_at: datetime | None = None,
    initiator: User | None = None,
) -> TourneyMatchLogEntry:
    """Assemble a tourney match log entry."""
    entry_id = generate_uuid7()

    if occurred_at is None:
        occurred_at = datetime.utcnow()

    return TourneyMatchLogEntry(
        id=entry_id,
        occurred_at=occurred_at,
        event_type=event_type,
        match_id=match_id,
        initiator=initiator,
        data=data,
    )
