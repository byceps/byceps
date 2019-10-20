"""
byceps.events.tourney
~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from dataclasses import dataclass

from .base import _BaseEvent


# tourney


@dataclass(frozen=True)
class _TourneyEvent(_BaseEvent):
    tourney_id: str


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
    match_id: str


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
    participant_id: str
    match_id: str


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
