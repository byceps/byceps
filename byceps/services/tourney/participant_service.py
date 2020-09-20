"""
byceps.services.tourney.participant_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Set

from .models.participant import Participant as DbParticipant
from .transfer.models import Participant


def get_participants_for_tourney(tourney_id: int) -> Set[Participant]:
    """Return the participants of the tourney."""
    participants = DbParticipant.query \
        .filter_by(tourney_id=tourney_id) \
        .all()

    return {_db_entity_to_participant(participant) for participant in participants}


def _db_entity_to_participant(participant: DbParticipant) -> Participant:
    logo_url = None

    return Participant(
        participant.id,
        participant.tourney_id,
        participant.title,
        logo_url,
    )
