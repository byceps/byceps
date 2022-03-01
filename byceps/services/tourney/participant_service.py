"""
byceps.services.tourney.participant_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from typing import Optional

from ...database import db

from .dbmodels.participant import Participant as DbParticipant
from . import tourney_service
from .transfer.models import Participant, ParticipantID, TourneyID


def create_participant(
    tourney_id: TourneyID, title: str, max_size: int
) -> Participant:
    """Create a participant."""
    tourney = tourney_service.get_tourney(tourney_id)

    participant = DbParticipant(tourney.id, title, max_size)

    db.session.add(participant)
    db.session.commit()

    return _db_entity_to_participant(participant)


def delete_participant(participant_id: ParticipantID) -> None:
    """Delete a participant."""
    participant = find_participant(participant_id)
    if participant is None:
        raise ValueError(f'Unknown participant ID "{participant_id}"')

    db.session.query(DbParticipant) \
        .filter_by(id=participant_id) \
        .delete()

    db.session.commit()


def find_participant(participant_id: ParticipantID) -> Optional[Participant]:
    """Return the participant with that id, or `None` if not found."""
    participant = db.session.get(DbParticipant, participant_id)

    if participant is None:
        return None

    return _db_entity_to_participant(participant)


def get_participants_for_tourney(tourney_id: TourneyID) -> set[Participant]:
    """Return the participants of the tourney."""
    participants = db.session \
        .query(DbParticipant) \
        .filter_by(tourney_id=tourney_id) \
        .all()

    return {
        _db_entity_to_participant(participant) for participant in participants
    }


def _db_entity_to_participant(participant: DbParticipant) -> Participant:
    logo_url = None

    return Participant(
        participant.id,
        participant.tourney_id,
        participant.title,
        logo_url,
    )
