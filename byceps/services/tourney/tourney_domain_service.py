"""
byceps.services.tourney.tourney_domain_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from byceps.services.party.models import Party
from byceps.services.tourney.log import tourney_log_serialization_service
from byceps.services.tourney.log.models import TourneyLogEntry
from byceps.services.user.models.user import User
from byceps.util.uuid import generate_uuid7

from .events import TourneyCreatedEvent
from .models import Tourney, TourneyID, TourneyCategory


def create_tourney(
    party: Party,
    creator: User,
    title: str,
    category: TourneyCategory,
    team_size: int,
    max_participant_count: int,
    starts_at: datetime,
    *,
    subtitle: str | None = None,
    logo_url: str | None = None,
    registration_open: bool = False,
) -> tuple[Tourney, TourneyCreatedEvent, TourneyLogEntry]:
    """Create a tourney."""
    tourney_id = TourneyID(generate_uuid7())
    occurred_at = datetime.utcnow()
    current_participant_count = 0

    tourney = Tourney(
        id=tourney_id,
        party_id=party.id,
        title=title,
        subtitle=subtitle,
        logo_url=logo_url,
        category_id=category.id,
        team_size=team_size,
        current_participant_count=current_participant_count,
        max_participant_count=max_participant_count,
        starts_at=starts_at,
        registration_open=registration_open,
    )

    event = _build_tourney_created_event(tourney, occurred_at, creator)

    log_entry = (
        tourney_log_serialization_service.serialize_tourney_created_event(event)
    )

    return tourney, event, log_entry


def _build_tourney_created_event(
    tourney: Tourney, occurred_at: datetime, creator: User
) -> TourneyCreatedEvent:
    return TourneyCreatedEvent(
        occurred_at=occurred_at,
        initiator=creator,
        tourney=tourney.to_basic_tourney(),
    )
