"""
byceps.services.tourney.tourney_participant_domain_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.util.uuid import generate_uuid7

from .models import Participant, ParticipantID, Tourney


def create_participant(tourney: Tourney, name: str) -> Participant:
    """Create a participant."""
    participant_id = ParticipantID(generate_uuid7())

    return Participant(
        id=participant_id,
        tourney_id=tourney.id,
        name=name,
        logo_url=None,
    )
