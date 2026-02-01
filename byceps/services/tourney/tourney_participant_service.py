"""
byceps.services.tourney.tourney_participant_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Sequence

from byceps.services.user import user_service
from byceps.services.user.models import User, UserID

from . import tourney_participant_domain_service, tourney_participant_repository
from .dbmodels.participant import DbParticipant
from .models import (
    Participant,
    ParticipantID,
    ParticipantMembership,
    ParticipantMembershipStatus,
    Tourney,
    TourneyID,
)


def create_participant(
    tourney: Tourney,
    name: str,
    manager: User,
    initiator: User,
) -> Participant:
    """Create a participant."""
    participant, event = tourney_participant_domain_service.create_participant(
        tourney, name, manager, initiator
    )

    created_at = event.occurred_at

    tourney_participant_repository.create_participant(participant, created_at)

    return participant


def delete_participant(participant_id: ParticipantID) -> None:
    """Delete a participant."""
    tourney_participant_repository.delete_participant(participant_id)


def find_participant(participant_id: ParticipantID) -> Participant | None:
    """Return the participant with that ID, or `None` if not found."""
    db_participant = tourney_participant_repository.find_participant(
        participant_id
    )

    if db_participant is None:
        return None

    managers_by_id = _get_managers_by_id([db_participant], include_avatars=True)

    return _db_entity_to_participant(db_participant, managers_by_id)


def get_participants_for_tourney(tourney_id: TourneyID) -> set[Participant]:
    """Return the participants of the tourney."""
    db_participants = (
        tourney_participant_repository.get_participants_for_tourney(tourney_id)
    )

    managers_by_id = _get_managers_by_id(db_participants, include_avatars=True)

    return {
        _db_entity_to_participant(db_participant, managers_by_id)
        for db_participant in db_participants
    }


def _get_managers_by_id(
    db_participants: Sequence[DbParticipant], *, include_avatars: bool = False
) -> dict[UserID, User]:
    manager_ids = {
        db_participant.manager_id for db_participant in db_participants
    }

    return user_service.get_users_indexed_by_id(
        manager_ids, include_avatars=include_avatars
    )


def _db_entity_to_participant(
    db_participant: DbParticipant, managers_by_id: dict[UserID, User]
) -> Participant:
    manager = managers_by_id[db_participant.manager_id]

    return Participant(
        id=db_participant.id,
        tourney_id=db_participant.tourney_id,
        name=db_participant.name,
        logo_url=None,
        manager=manager,
    )


def add_player_to_participant(
    tourney: Tourney,
    participant: Participant,
    player: User,
    status: ParticipantMembershipStatus,
    initiator: User,
) -> ParticipantMembership:
    """Add a player to a participant."""
    membership, event = (
        tourney_participant_domain_service.add_player_to_participant(
            tourney, participant, player, status, initiator
        )
    )

    tourney_participant_repository.add_player_to_participant(membership)

    return membership


def remove_player_from_participant(
    tourney: Tourney,
    participant: Participant,
    membership: ParticipantMembership,
    initiator: User,
) -> None:
    """Remove a player from a participant."""
    event = tourney_participant_domain_service.delete_participant_membership(
        tourney, participant, membership, initiator
    )

    tourney_participant_repository.delete_participant_membership(membership.id)
