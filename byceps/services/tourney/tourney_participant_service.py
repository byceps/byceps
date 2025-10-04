"""
byceps.services.tourney.tourney_participant_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.services.user.models.user import User

from . import tourney_participant_domain_service, tourney_participant_repository
from .dbmodels.participant import DbParticipant
from .models import Participant, ParticipantID, Tourney, TourneyID


def create_participant(
    tourney: Tourney, name: str, initiator: User
) -> Participant:
    """Create a participant."""
    participant, event = tourney_participant_domain_service.create_participant(
        tourney, name, initiator
    )

    created_at = event.occurred_at

    tourney_participant_repository.create_participant(
        participant, created_at, initiator.id
    )

    return participant


def delete_participant(participant_id: ParticipantID) -> None:
    """Delete a participant."""
    tourney_participant_repository.delete_participant(participant_id)


def find_participant(participant_id: ParticipantID) -> Participant | None:
    """Return the participant with that id, or `None` if not found."""
    db_participant = tourney_participant_repository.find_participant(
        participant_id
    )

    if db_participant is None:
        return None

    return _db_entity_to_participant(db_participant)


def get_participants_for_tourney(tourney_id: TourneyID) -> set[Participant]:
    """Return the participants of the tourney."""
    db_participants = (
        tourney_participant_repository.get_participants_for_tourney(tourney_id)
    )

    return {
        _db_entity_to_participant(db_participant)
        for db_participant in db_participants
    }


def _db_entity_to_participant(db_participant: DbParticipant) -> Participant:
    return Participant(
        id=db_participant.id,
        tourney_id=db_participant.tourney_id,
        name=db_participant.name,
        logo_url=None,
    )
