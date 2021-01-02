"""
byceps.services.tourney.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import NewType, Optional
from uuid import UUID

from ....typing import PartyID

from ...user.transfer.models import User


TourneyCategoryID = NewType('TourneyCategoryID', UUID)


@dataclass(frozen=True)
class TourneyCategory:
    id: TourneyCategoryID
    party_id: PartyID
    position: int
    title: str


TourneyID = NewType('TourneyID', UUID)


@dataclass(frozen=True)
class Tourney:
    id: TourneyID
    party_id: PartyID
    title: str
    subtitle: Optional[str]
    logo_url: Optional[str]
    category_id: TourneyCategoryID
    current_participant_count: int
    max_participant_count: int
    starts_at: datetime


@dataclass(frozen=True)
class TourneyWithCategory(Tourney):
    category: TourneyCategory

    @classmethod
    def from_tourney_and_category(
        cls: TourneyWithCategory,
        tourney: Tourney,
        category: TourneyCategory,
        current_participant_count: int,
    ) -> TourneyWithCategory:
        return cls(
            id=tourney.id,
            party_id=tourney.party_id,
            title=tourney.title,
            subtitle=tourney.subtitle,
            logo_url=tourney.logo_url,
            category_id=tourney.category_id,
            current_participant_count=current_participant_count,
            max_participant_count=tourney.max_participant_count,
            starts_at=tourney.starts_at,
            category=category,
        )


MatchID = NewType('MatchID', UUID)


MatchCommentID = NewType('MatchCommentID', UUID)


ParticipantID = NewType('ParticipantID', UUID)


@dataclass(frozen=True)
class Participant:
    id: ParticipantID
    tourney_id: TourneyID
    title: str
    logo_url: Optional[str]


@dataclass(frozen=True)
class Match:
    id: MatchID


@dataclass(frozen=True)
class MatchComment:
    id: MatchCommentID
    match_id: MatchID
    created_at: datetime
    created_by: User
    body_text: str
    body_html: str
    last_edited_at: Optional[datetime]
    last_edited_by: Optional[User]
    hidden: bool
    hidden_at: Optional[datetime]
    hidden_by: Optional[User]
