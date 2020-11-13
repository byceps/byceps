"""
byceps.events.tourney
~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from typing import Optional

from .base import _BaseEvent


# tourney


@dataclass(frozen=True)
class _TourneyEvent(_BaseEvent):
    tourney_id: str
    tourney_title: str


@dataclass(frozen=True)
class TourneyStarted(_TourneyEvent):
    pass


@dataclass(frozen=True)
class TourneyPaused(_TourneyEvent):
    pass


@dataclass(frozen=True)
class TourneyCanceled(_TourneyEvent):
    pass


@dataclass(frozen=True)
class TourneyFinished(_TourneyEvent):
    pass


# match


@dataclass(frozen=True)
class _TourneyMatchEvent(_BaseEvent):
    tourney_id: str
    tourney_title: str
    match_id: str
    participant1_id: Optional[str]
    participant1_name: Optional[str]
    participant2_id: Optional[str]
    participant2_name: Optional[str]


@dataclass(frozen=True)
class TourneyMatchReady(_TourneyMatchEvent):
    pass


@dataclass(frozen=True)
class TourneyMatchReset(_TourneyMatchEvent):
    pass


@dataclass(frozen=True)
class TourneyMatchScoreSubmitted(_TourneyMatchEvent):
    pass


@dataclass(frozen=True)
class TourneyMatchScoreConfirmed(_TourneyMatchEvent):
    pass


@dataclass(frozen=True)
class TourneyMatchScoreRandomized(_TourneyMatchEvent):
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
class TourneyParticipantReady(_TourneyParticipantEvent):
    pass


@dataclass(frozen=True)
class TourneyParticipantEliminated(_TourneyParticipantEvent):
    pass


@dataclass(frozen=True)
class TourneyParticipantWarned(_TourneyParticipantEvent):
    pass


@dataclass(frozen=True)
class TourneyParticipantDisqualified(_TourneyParticipantEvent):
    pass
