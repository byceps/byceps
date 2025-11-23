"""
byceps.services.tourney.events
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass

from byceps.services.core.events import _BaseEvent, EventUser

from .models import (
    MatchID,
    ParticipantID,
    ParticipantMembershipStatus,
    TourneyID,
)


@dataclass(frozen=True, kw_only=True)
class EventTourney:
    id: TourneyID
    title: str


@dataclass(frozen=True, kw_only=True)
class EventTourneyParticipant:
    id: ParticipantID
    name: str


@dataclass(frozen=True, kw_only=True)
class _BaseTourneyEvent(_BaseEvent):
    tourney: EventTourney


# tourney


@dataclass(frozen=True, kw_only=True)
class _TourneyEvent(_BaseTourneyEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class TourneyCreatedEvent(_TourneyEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class TourneyRegistrationOpenedEvent(_TourneyEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class TourneyRegistrationClosedEvent(_TourneyEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class TourneyStartedEvent(_TourneyEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class TourneyPausedEvent(_TourneyEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class TourneyContinuedEvent(_TourneyEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class TourneyCanceledEvent(_TourneyEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class TourneyFinishedEvent(_TourneyEvent):
    pass


# participant


@dataclass(frozen=True, kw_only=True)
class _TourneyParticipantEvent(_BaseTourneyEvent):
    participant: EventTourneyParticipant


@dataclass(frozen=True, kw_only=True)
class TourneyParticipantCreatedEvent(_TourneyParticipantEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class TourneyParticipantMembershipCreatedEvent(_TourneyParticipantEvent):
    player: EventUser
    status: ParticipantMembershipStatus


@dataclass(frozen=True, kw_only=True)
class TourneyParticipantMembershipDeletedEvent(_TourneyParticipantEvent):
    player: EventUser


# match


@dataclass(frozen=True, kw_only=True)
class _TourneyMatchEvent(_BaseTourneyEvent):
    match_id: MatchID
    participant1: EventTourneyParticipant | None
    participant2: EventTourneyParticipant | None


@dataclass(frozen=True, kw_only=True)
class TourneyMatchReadyEvent(_TourneyMatchEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class TourneyMatchResetEvent(_TourneyMatchEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class TourneyMatchScoreSubmittedEvent(_TourneyMatchEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class TourneyMatchScoreConfirmedEvent(_TourneyMatchEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class TourneyMatchScoreRandomizedEvent(_TourneyMatchEvent):
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
