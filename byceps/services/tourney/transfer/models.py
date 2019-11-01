"""
byceps.services.tourney.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import NewType
from uuid import UUID

from attr import attrs


TourneyCategoryID = NewType('TourneyCategoryID', UUID)


TourneyID = NewType('TourneyID', UUID)


MatchID = NewType('MatchID', UUID)


MatchCommentID = NewType('MatchCommentID', UUID)


ParticipantID = NewType('ParticipantID', UUID)


@attrs(auto_attribs=True, frozen=True, slots=True)
class Match:
    id: MatchID
