"""
byceps.services.tourney.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import NewType, Self
from uuid import UUID

from byceps.services.party.models import PartyID
from byceps.services.user.models.user import User


TourneyCategoryID = NewType('TourneyCategoryID', UUID)


@dataclass(frozen=True, kw_only=True)
class TourneyCategory:
    id: TourneyCategoryID
    party_id: PartyID
    position: int
    title: str


TourneyID = NewType('TourneyID', UUID)


@dataclass(frozen=True, kw_only=True)
class BasicTourney:
    id: TourneyID
    title: str


@dataclass(frozen=True, kw_only=True)
class Tourney:
    id: TourneyID
    party_id: PartyID
    title: str
    subtitle: str | None
    logo_url: str | None
    category_id: TourneyCategoryID
    team_size: int
    current_participant_count: int
    max_participant_count: int
    starts_at: datetime
    registration_open: bool

    def to_basic_tourney(self) -> BasicTourney:
        return BasicTourney(
            id=self.id,
            title=self.title,
        )


@dataclass(frozen=True, kw_only=True)
class TourneyWithCategory(Tourney):
    category: TourneyCategory

    @classmethod
    def from_tourney_and_category(
        cls,
        tourney: Tourney,
        category: TourneyCategory,
        current_participant_count: int,
    ) -> Self:
        return cls(
            id=tourney.id,
            party_id=tourney.party_id,
            title=tourney.title,
            subtitle=tourney.subtitle,
            logo_url=tourney.logo_url,
            category_id=tourney.category_id,
            team_size=tourney.team_size,
            current_participant_count=current_participant_count,
            max_participant_count=tourney.max_participant_count,
            starts_at=tourney.starts_at,
            registration_open=tourney.registration_open,
            category=category,
        )


MatchID = NewType('MatchID', UUID)


MatchCommentID = NewType('MatchCommentID', UUID)


ParticipantID = NewType('ParticipantID', UUID)


@dataclass(frozen=True, kw_only=True)
class Participant:
    id: ParticipantID
    tourney_id: TourneyID
    name: str
    logo_url: str | None
    manager: User


ParticipantMembershipStatus = Enum('ParticipantMembershipStatus', ['approved'])


@dataclass(frozen=True, kw_only=True)
class ParticipantMembership:
    id: UUID
    participant_id: ParticipantID
    player: User
    status: ParticipantMembershipStatus


@dataclass(frozen=True, kw_only=True)
class Match:
    id: MatchID


@dataclass(frozen=True, kw_only=True)
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
