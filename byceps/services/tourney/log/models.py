"""
byceps.services.tourney.log.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from byceps.services.tourney.models import BasicTourney, MatchID, ParticipantID
from byceps.services.user.models.user import User


LogEntryData = dict[str, Any]


@dataclass(frozen=True, kw_only=True)
class TourneyLogEntry:
    id: UUID
    occurred_at: datetime
    event_type: str
    tourney: BasicTourney
    initiator: User | None
    data: LogEntryData


@dataclass(frozen=True, kw_only=True)
class TourneyParticipantLogEntry:
    id: UUID
    occurred_at: datetime
    event_type: str
    participant_id: ParticipantID
    initiator: User | None
    data: LogEntryData


@dataclass(frozen=True, kw_only=True)
class TourneyMatchLogEntry:
    id: UUID
    occurred_at: datetime
    event_type: str
    match_id: MatchID
    initiator: User | None
    data: LogEntryData
