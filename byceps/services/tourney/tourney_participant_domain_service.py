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
)
from .models import Participant, ParticipantID, Tourney


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
