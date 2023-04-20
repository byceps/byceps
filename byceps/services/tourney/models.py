"""
byceps.services.tourney.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import NewType
from uuid import UUID

from byceps.services.user.models.user import User
from byceps.typing import PartyID


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
    subtitle: str | None
    logo_url: str | None
    category_id: TourneyCategoryID
    current_participant_count: int
    max_participant_count: int
    starts_at: datetime


@dataclass(frozen=True)
class TourneyWithCategory(Tourney):
    category: TourneyCategory

    @classmethod
    def from_tourney_and_category(
        cls,
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
    logo_url: str | None


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
    last_edited_at: datetime | None
    last_edited_by: User | None
    hidden: bool
    hidden_at: datetime | None
    hidden_by: User | None
