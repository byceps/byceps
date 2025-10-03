"""
byceps.services.tourney.tourney_participant_repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import delete, select

from byceps.database import db
from byceps.services.user.models.user import UserID

from .dbmodels.participant import DbParticipant
from .models import Participant, ParticipantID, TourneyID


def create_participant(
    participant: Participant,
    created_at: datetime,
    creator_id: UserID,
    max_size: int,
) -> None:
    """Create a participant."""
    db_participant = DbParticipant(
        participant.id,
        participant.tourney_id,
        created_at,
        creator_id,
        participant.name,
        max_size,
    )

    db.session.add(db_participant)
    db.session.commit()


def delete_participant(participant_id: ParticipantID) -> None:
    """Delete a participant."""
    participant = find_participant(participant_id)
    if participant is None:
        raise ValueError(f'Unknown participant ID "{participant_id}"')

    db.session.execute(delete(DbParticipant).filter_by(id=participant.id))
    db.session.commit()


def find_participant(participant_id: ParticipantID) -> DbParticipant | None:
    """Return the participant with that id, or `None` if not found."""
    return db.session.get(DbParticipant, participant_id)


def get_participants_for_tourney(
    tourney_id: TourneyID,
) -> Sequence[DbParticipant]:
    """Return the participants of the tourney."""
    return db.session.scalars(
        select(DbParticipant).filter_by(tourney_id=tourney_id)
    ).all()
