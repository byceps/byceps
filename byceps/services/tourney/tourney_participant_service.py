"""
byceps.services.tourney.tourney_participant_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations


from sqlalchemy import delete, select

from byceps.database import db

from . import tourney_service
from .dbmodels.participant import DbParticipant
from .models import Participant, ParticipantID, TourneyID


def create_participant(
    tourney_id: TourneyID, title: str, max_size: int
) -> Participant:
    """Create a participant."""
    tourney = tourney_service.get_tourney(tourney_id)

    db_participant = DbParticipant(tourney.id, title, max_size)

    db.session.add(db_participant)
    db.session.commit()

    return _db_entity_to_participant(db_participant)


def delete_participant(participant_id: ParticipantID) -> None:
    """Delete a participant."""
    participant = find_participant(participant_id)
    if participant is None:
        raise ValueError(f'Unknown participant ID "{participant_id}"')

    db.session.execute(delete(DbParticipant).filter_by(id=participant.id))
    db.session.commit()


def find_participant(participant_id: ParticipantID) -> Participant | None:
    """Return the participant with that id, or `None` if not found."""
    db_participant = db.session.get(DbParticipant, participant_id)

    if db_participant is None:
        return None

    return _db_entity_to_participant(db_participant)


def get_participants_for_tourney(tourney_id: TourneyID) -> set[Participant]:
    """Return the participants of the tourney."""
    db_participants = db.session.scalars(
        select(DbParticipant).filter_by(tourney_id=tourney_id)
    ).all()

    return {
        _db_entity_to_participant(db_participant)
        for db_participant in db_participants
    }


def _db_entity_to_participant(db_participant: DbParticipant) -> Participant:
    return Participant(
        id=db_participant.id,
        tourney_id=db_participant.tourney_id,
        title=db_participant.title,
        logo_url=None,
    )
