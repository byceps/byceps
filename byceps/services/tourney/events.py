"""
byceps.services.tourney.events
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from typing import Self

from byceps.services.core.events import _BaseEvent
from byceps.services.user.models.user import User

from .models import (
    BasicTourney,
    MatchID,
    Participant,
    ParticipantID,
    ParticipantMembershipStatus,
)


@dataclass(frozen=True, kw_only=True)
class EventTourneyParticipant:
    id: ParticipantID
    name: str

    @classmethod
    def from_participant(cls, participant: Participant) -> Self:
        return cls(
            id=participant.id,
            name=participant.name,
        )


@dataclass(frozen=True, kw_only=True)
class _BaseTourneyEvent(_BaseEvent):
    tourney: BasicTourney


# tourney


@dataclass(frozen=True, kw_only=True)
class TourneyEvent(_BaseTourneyEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class TourneyCreatedEvent(TourneyEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class TourneyRegistrationOpenedEvent(TourneyEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class TourneyRegistrationClosedEvent(TourneyEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class TourneyStartedEvent(TourneyEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class TourneyPausedEvent(TourneyEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class TourneyContinuedEvent(TourneyEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class TourneyCanceledEvent(TourneyEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class TourneyFinishedEvent(TourneyEvent):
    pass


# participant


@dataclass(frozen=True, kw_only=True)
class TourneyParticipantEvent(_BaseTourneyEvent):
    participant: EventTourneyParticipant


@dataclass(frozen=True, kw_only=True)
class TourneyParticipantCreatedEvent(TourneyParticipantEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class TourneyParticipantMembershipCreatedEvent(TourneyParticipantEvent):
    player: User
    status: ParticipantMembershipStatus


@dataclass(frozen=True, kw_only=True)
class TourneyParticipantMembershipDeletedEvent(TourneyParticipantEvent):
    player: User


# match


@dataclass(frozen=True, kw_only=True)
class TourneyMatchEvent(_BaseTourneyEvent):
    match_id: MatchID
    participant1: EventTourneyParticipant | None
    participant2: EventTourneyParticipant | None


@dataclass(frozen=True, kw_only=True)
class TourneyMatchReadyEvent(TourneyMatchEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class TourneyMatchResetEvent(TourneyMatchEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class TourneyMatchScoreSubmittedEvent(TourneyMatchEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class TourneyMatchScoreConfirmedEvent(TourneyMatchEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class TourneyMatchScoreRandomizedEvent(TourneyMatchEvent):
    pass


# match participant


@dataclass(frozen=True, kw_only=True)
class _TourneyMatchParticipantEvent(_BaseTourneyEvent):
    match_id: MatchID
    participant: EventTourneyParticipant


@dataclass(frozen=True, kw_only=True)
class TourneyMatchParticipantReadyEvent(_TourneyMatchParticipantEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class TourneyMatchParticipantEliminatedEvent(_TourneyMatchParticipantEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class TourneyMatchParticipantWarnedEvent(_TourneyMatchParticipantEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class TourneyMatchParticipantDisqualifiedEvent(_TourneyMatchParticipantEvent):
    pass
