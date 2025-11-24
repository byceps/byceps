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
    TourneyEvent,
    TourneyFinishedEvent,
    TourneyPausedEvent,
    TourneyRegistrationClosedEvent,
    TourneyRegistrationOpenedEvent,
    TourneyStartedEvent,
)
from byceps.util.result import Err, Ok, Result
from byceps.util.uuid import generate_uuid7

from .models import TourneyLogEntry


# tourney


def serialize_tourney_event(
    event: TourneyEvent,
) -> Result[TourneyLogEntry, str]:
    match event:
        case TourneyCreatedEvent():
            return Ok(serialize_tourney_created_event(event))
        case TourneyRegistrationOpenedEvent():
            return Ok(serialize_tourney_registration_opened_event(event))
        case TourneyRegistrationClosedEvent():
            return Ok(serialize_tourney_registration_closed_event(event))
        case TourneyStartedEvent():
            return Ok(serialize_tourney_started_event(event))
        case TourneyPausedEvent():
            return Ok(serialize_tourney_paused_event(event))
        case TourneyContinuedEvent():
            return Ok(serialize_tourney_continued_event(event))
        case TourneyCanceledEvent():
            return Ok(serialize_tourney_canceled_event(event))
        case TourneyFinishedEvent():
            return Ok(serialize_tourney_finished_event(event))
        case _:
            return Err(f'Could not serialize event: {event!r}')


def serialize_tourney_created_event(
    event: TourneyCreatedEvent,
) -> TourneyLogEntry:
    entry_id = generate_uuid7()

    return TourneyLogEntry(
        id=entry_id,
        occurred_at=event.occurred_at,
        event_type='tourney-created',
        tourney=event.tourney,
        initiator=event.initiator,
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
        tourney=event.tourney,
        initiator=event.initiator,
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
        tourney=event.tourney,
        initiator=event.initiator,
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
        tourney=event.tourney,
        initiator=event.initiator,
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
        tourney=event.tourney,
        initiator=event.initiator,
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
        tourney=event.tourney,
        initiator=event.initiator,
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
        tourney=event.tourney,
        initiator=event.initiator,
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
        tourney=event.tourney,
        initiator=event.initiator,
        data={},
    )
