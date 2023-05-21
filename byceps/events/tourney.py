"""
byceps.events.tourney
~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from dataclasses import dataclass

from .base import _BaseEvent


# tourney


@dataclass(frozen=True)
class _TourneyEvent(_BaseEvent):
    tourney_id: str
    tourney_title: str


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
class _TourneyMatchEvent(_BaseEvent):
    tourney_id: str
    tourney_title: str
    match_id: str
    participant1_id: str | None
    participant1_name: str | None
    participant2_id: str | None
    participant2_name: str | None


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
class _TourneyParticipantEvent(_BaseEvent):
    tourney_id: str
    tourney_title: str
    match_id: str
    participant_id: str
    participant_name: str


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
