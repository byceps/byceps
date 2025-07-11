"""
byceps.services.tourney.events
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass

from byceps.services.core.events import _BaseEvent


@dataclass(frozen=True, kw_only=True)
class EventTourney:
    id: str
    title: str


@dataclass(frozen=True, kw_only=True)
class EventTourneyParticipant:
    id: str
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
class TourneyStartedEvent(_TourneyEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class TourneyPausedEvent(_TourneyEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class TourneyCanceledEvent(_TourneyEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class TourneyFinishedEvent(_TourneyEvent):
    pass


# match


@dataclass(frozen=True, kw_only=True)
class _TourneyMatchEvent(_BaseTourneyEvent):
    match_id: str
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


# participant


@dataclass(frozen=True, kw_only=True)
class _TourneyParticipantEvent(_BaseTourneyEvent):
    match_id: str
    participant: EventTourneyParticipant


@dataclass(frozen=True, kw_only=True)
class TourneyParticipantReadyEvent(_TourneyParticipantEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class TourneyParticipantEliminatedEvent(_TourneyParticipantEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class TourneyParticipantWarnedEvent(_TourneyParticipantEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class TourneyParticipantDisqualifiedEvent(_TourneyParticipantEvent):
    pass
