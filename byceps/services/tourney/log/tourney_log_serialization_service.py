"""
byceps.services.tourney.log.tourney_log_serialization_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.services.tourney.events import (
    TourneyCanceledEvent,
    TourneyContinuedEvent,
    TourneyCreatedEvent,
    TourneyFinishedEvent,
    TourneyPausedEvent,
    TourneyRegistrationClosedEvent,
    TourneyRegistrationOpenedEvent,
    TourneyStartedEvent,
)
from byceps.util.uuid import generate_uuid7

from .models import TourneyLogEntry


# tourney


def serialize_tourney_created_event(
    event: TourneyCreatedEvent,
) -> TourneyLogEntry:
    entry_id = generate_uuid7()

    return TourneyLogEntry(
        id=entry_id,
        occurred_at=event.occurred_at,
        event_type='tourney-created',
        tourney_id=event.tourney.id,
        initiator_id=event.initiator.id if event.initiator else None,
        data={},
    )


def serialize_tourney_registration_opened_event(
    event: TourneyRegistrationOpenedEvent,
) -> TourneyLogEntry:
    entry_id = generate_uuid7()

    return TourneyLogEntry(
        id=entry_id,
        occurred_at=event.occurred_at,
        event_type='tourney-registration-opened',
        tourney_id=event.tourney.id,
        initiator_id=event.initiator.id if event.initiator else None,
        data={},
    )


def serialize_tourney_registration_closed_event(
    event: TourneyRegistrationClosedEvent,
) -> TourneyLogEntry:
    entry_id = generate_uuid7()

    return TourneyLogEntry(
        id=entry_id,
        occurred_at=event.occurred_at,
        event_type='tourney-registration-closed',
        tourney_id=event.tourney.id,
        initiator_id=event.initiator.id if event.initiator else None,
        data={},
    )


def serialize_tourney_started_event(
    event: TourneyStartedEvent,
) -> TourneyLogEntry:
    entry_id = generate_uuid7()

    return TourneyLogEntry(
        id=entry_id,
        occurred_at=event.occurred_at,
        event_type='tourney-started',
        tourney_id=event.tourney.id,
        initiator_id=event.initiator.id if event.initiator else None,
        data={},
    )


def serialize_tourney_paused_event(
    event: TourneyPausedEvent,
) -> TourneyLogEntry:
    entry_id = generate_uuid7()

    return TourneyLogEntry(
        id=entry_id,
        occurred_at=event.occurred_at,
        event_type='tourney-paused',
        tourney_id=event.tourney.id,
        initiator_id=event.initiator.id if event.initiator else None,
        data={},
    )


def serialize_tourney_continued_event(
    event: TourneyContinuedEvent,
) -> TourneyLogEntry:
    entry_id = generate_uuid7()

    return TourneyLogEntry(
        id=entry_id,
        occurred_at=event.occurred_at,
        event_type='tourney-continued',
        tourney_id=event.tourney.id,
        initiator_id=event.initiator.id if event.initiator else None,
        data={},
    )


def serialize_tourney_canceled_event(
    event: TourneyCanceledEvent,
) -> TourneyLogEntry:
    entry_id = generate_uuid7()

    return TourneyLogEntry(
        id=entry_id,
        occurred_at=event.occurred_at,
        event_type='tourney-canceled',
        tourney_id=event.tourney.id,
        initiator_id=event.initiator.id if event.initiator else None,
        data={},
    )


def serialize_tourney_finished_event(
    event: TourneyFinishedEvent,
) -> TourneyLogEntry:
    entry_id = generate_uuid7()

    return TourneyLogEntry(
        id=entry_id,
        occurred_at=event.occurred_at,
        event_type='tourney-finished',
        tourney_id=event.tourney.id,
        initiator_id=event.initiator.id if event.initiator else None,
        data={},
    )
