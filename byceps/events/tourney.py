"""
byceps.events.tourney
~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass

from byceps.services.core.events import _BaseEvent


@dataclass(frozen=True)
class EventTourney:
    id: str
    title: str


@dataclass(frozen=True)
class EventTourneyParticipant:
    id: str
    name: str


@dataclass(frozen=True)
class _BaseTourneyEvent(_BaseEvent):
    tourney: EventTourney


# tourney


@dataclass(frozen=True)
class _TourneyEvent(_BaseTourneyEvent):
    pass


@dataclass(frozen=True)
class TourneyCreatedEvent(_TourneyEvent):
    pass


@dataclass(frozen=True)
class TourneyStartedEvent(_TourneyEvent):
    pass


@dataclass(frozen=True)
class TourneyPausedEvent(_TourneyEvent):
    pass


@dataclass(frozen=True)
class TourneyCanceledEvent(_TourneyEvent):
    pass


@dataclass(frozen=True)
class TourneyFinishedEvent(_TourneyEvent):
    pass


# match


@dataclass(frozen=True)
class _TourneyMatchEvent(_BaseTourneyEvent):
    match_id: str
    participant1: EventTourneyParticipant | None
    participant2: EventTourneyParticipant | None


@dataclass(frozen=True)
class TourneyMatchReadyEvent(_TourneyMatchEvent):
    pass


@dataclass(frozen=True)
class TourneyMatchResetEvent(_TourneyMatchEvent):
    pass


@dataclass(frozen=True)
class TourneyMatchScoreSubmittedEvent(_TourneyMatchEvent):
    pass


@dataclass(frozen=True)
class TourneyMatchScoreConfirmedEvent(_TourneyMatchEvent):
    pass


@dataclass(frozen=True)
class TourneyMatchScoreRandomizedEvent(_TourneyMatchEvent):
    pass


# participant


@dataclass(frozen=True)
class _TourneyParticipantEvent(_BaseTourneyEvent):
    match_id: str
    participant: EventTourneyParticipant


@dataclass(frozen=True)
class TourneyParticipantReadyEvent(_TourneyParticipantEvent):
    pass


@dataclass(frozen=True)
class TourneyParticipantEliminatedEvent(_TourneyParticipantEvent):
    pass


@dataclass(frozen=True)
class TourneyParticipantWarnedEvent(_TourneyParticipantEvent):
    pass


@dataclass(frozen=True)
class TourneyParticipantDisqualifiedEvent(_TourneyParticipantEvent):
    pass
