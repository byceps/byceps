"""
byceps.events.tourney
~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from dataclasses import dataclass

from ..services.tourney.transfer.models import MatchID, TeamID, TourneyID

from .base import _BaseEvent


# tourney


@dataclass(frozen=True)
class _TourneyEvent(_BaseEvent):
    tourney_id: TourneyID


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
    match_id: MatchID


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


# team


@dataclass(frozen=True)
class _TourneyTeamEvent(_BaseEvent):
    team_id: TeamID


@dataclass(frozen=True)
class TourneyTeamReady(_TourneyTeamEvent):
    pass


@dataclass(frozen=True)
class TourneyTeamEliminated(_TourneyTeamEvent):
    pass


@dataclass(frozen=True)
class TourneyTeamWarned(_TourneyTeamEvent):
    pass


@dataclass(frozen=True)
class TourneyTeamDisqualified(_TourneyTeamEvent):
    pass
