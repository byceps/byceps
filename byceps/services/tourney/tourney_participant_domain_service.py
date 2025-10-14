"""
byceps.services.tourney.tourney_participant_domain_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from byceps.services.core.events import EventUser
from byceps.services.user.models.user import User
from byceps.util.uuid import generate_uuid7

from .events import (
    EventTourney,
    EventTourneyParticipant,
    TourneyParticipantCreatedEvent,
    TourneyParticipantMembershipCreatedEvent,
    TourneyParticipantMembershipDeletedEvent,
)
from .models import (
    Participant,
    ParticipantID,
    ParticipantMembership,
    ParticipantMembershipStatus,
    Tourney,
)


def create_participant(
    tourney: Tourney,
    name: str,
    manager: User,
    initiator: User,
) -> tuple[Participant, TourneyParticipantCreatedEvent]:
    """Create a participant."""
    participant_id = ParticipantID(generate_uuid7())
    occurred_at = datetime.utcnow()

    participant = Participant(
        id=participant_id,
        tourney_id=tourney.id,
        name=name,
        logo_url=None,
        manager=manager,
    )

    event = _build_participant_created_event(
        tourney, participant, occurred_at, initiator
    )

    return participant, event


def _build_participant_created_event(
    tourney: Tourney,
    participant: Participant,
    occurred_at: datetime,
    initiator: User,
) -> TourneyParticipantCreatedEvent:
    return TourneyParticipantCreatedEvent(
        occurred_at=occurred_at,
        initiator=EventUser.from_user(initiator),
        tourney=EventTourney(id=tourney.id, title=tourney.title),
        participant=EventTourneyParticipant(
            id=participant.id,
            name=participant.name,
        ),
    )


def add_player_to_participant(
    tourney: Tourney,
    participant: Participant,
    player: User,
    status: ParticipantMembershipStatus,
    initiator: User,
) -> tuple[ParticipantMembership, TourneyParticipantMembershipCreatedEvent]:
    """Add a player to a participant."""
    membership_id = generate_uuid7()
    occurred_at = datetime.utcnow()

    membership = ParticipantMembership(
        id=membership_id,
        participant_id=participant.id,
        player=player,
        status=status,
    )

    event = _build_participant_membership_created_event(
        tourney, participant, membership, occurred_at, initiator
    )

    return membership, event


def _build_participant_membership_created_event(
    tourney: Tourney,
    participant: Participant,
    membership: ParticipantMembership,
    occurred_at: datetime,
    initiator: User,
) -> TourneyParticipantMembershipCreatedEvent:
    return TourneyParticipantMembershipCreatedEvent(
        occurred_at=occurred_at,
        initiator=EventUser.from_user(initiator),
        tourney=EventTourney(id=tourney.id, title=tourney.title),
        participant=EventTourneyParticipant(
            id=participant.id,
            name=participant.name,
        ),
        player=EventUser.from_user(membership.player),
        status=membership.status,
    )


def delete_participant_membership(
    tourney: Tourney,
    participant: Participant,
    membership: ParticipantMembership,
    initiator: User,
) -> TourneyParticipantMembershipDeletedEvent:
    """Remove a player from a participant."""
    occurred_at = datetime.utcnow()

    event = _build_participant_membership_deleted_event(
        tourney, participant, membership, occurred_at, initiator
    )

    return event


def _build_participant_membership_deleted_event(
    tourney: Tourney,
    participant: Participant,
    membership: ParticipantMembership,
    occurred_at: datetime,
    initiator: User,
) -> TourneyParticipantMembershipDeletedEvent:
    return TourneyParticipantMembershipDeletedEvent(
        occurred_at=occurred_at,
        initiator=EventUser.from_user(initiator),
        tourney=EventTourney(id=tourney.id, title=tourney.title),
        participant=EventTourneyParticipant(
            id=participant.id,
            name=participant.name,
        ),
        player=EventUser.from_user(membership.player),
    )
