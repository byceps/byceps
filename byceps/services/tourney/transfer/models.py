"""
byceps.services.tourney.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from dataclasses import dataclass
from typing import NewType
from uuid import UUID


TourneyCategoryID = NewType('TourneyCategoryID', UUID)


TourneyID = NewType('TourneyID', UUID)


MatchID = NewType('MatchID', UUID)


MatchCommentID = NewType('MatchCommentID', UUID)


ParticipantID = NewType('ParticipantID', UUID)


@dataclass(frozen=True)
class Match:
    id: MatchID
