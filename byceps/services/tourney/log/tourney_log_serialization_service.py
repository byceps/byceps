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


def deserialize_tourney_event(
    log_entry: TourneyLogEntry,
) -> Result[TourneyEvent, str]:
    match log_entry.event_type:
        case 'tourney-created':
            return Ok(deserialize_tourney_created_event(log_entry))
        case 'tourney-registration-opened':
            return Ok(deserialize_tourney_registration_opened_event(log_entry))
        case 'tourney-registration-closed':
            return Ok(deserialize_tourney_registration_closed_event(log_entry))
        case 'tourney-started':
            return Ok(deserialize_tourney_started_event(log_entry))
        case 'tourney-paused':
            return Ok(deserialize_tourney_paused_event(log_entry))
        case 'tourney-continued':
            return Ok(deserialize_tourney_continued_event(log_entry))
        case 'tourney-canceled':
            return Ok(deserialize_tourney_canceled_event(log_entry))
        case 'tourney-finished':
            return Ok(deserialize_tourney_finished_event(log_entry))
        case _:
            return Err(
                f'Could not deserialize event type from log entry: {log_entry!r}'
            )


def serialize_tourney_created_event(
    event: TourneyCreatedEvent,
) -> TourneyLogEntry:
    return _serialize_tourney_event(event, 'tourney-created')


def deserialize_tourney_created_event(
    log_entry: TourneyLogEntry,
) -> TourneyCreatedEvent:
    return TourneyCreatedEvent(
        occurred_at=log_entry.occurred_at,
        initiator=log_entry.initiator,
        tourney=log_entry.tourney,
    )


def serialize_tourney_registration_opened_event(
    event: TourneyRegistrationOpenedEvent,
) -> TourneyLogEntry:
    return _serialize_tourney_event(event, 'tourney-registration-opened')


def deserialize_tourney_registration_opened_event(
    log_entry: TourneyLogEntry,
) -> TourneyRegistrationOpenedEvent:
    return TourneyRegistrationOpenedEvent(
        occurred_at=log_entry.occurred_at,
        initiator=log_entry.initiator,
        tourney=log_entry.tourney,
    )


def serialize_tourney_registration_closed_event(
    event: TourneyRegistrationClosedEvent,
) -> TourneyLogEntry:
    return _serialize_tourney_event(event, 'tourney-registration-closed')


def deserialize_tourney_registration_closed_event(
    log_entry: TourneyLogEntry,
) -> TourneyRegistrationClosedEvent:
    return TourneyRegistrationClosedEvent(
        occurred_at=log_entry.occurred_at,
        initiator=log_entry.initiator,
        tourney=log_entry.tourney,
    )


def serialize_tourney_started_event(
    event: TourneyStartedEvent,
) -> TourneyLogEntry:
    return _serialize_tourney_event(event, 'tourney-started')


def deserialize_tourney_started_event(
    log_entry: TourneyLogEntry,
) -> TourneyStartedEvent:
    return TourneyStartedEvent(
        occurred_at=log_entry.occurred_at,
        initiator=log_entry.initiator,
        tourney=log_entry.tourney,
    )


def serialize_tourney_paused_event(
    event: TourneyPausedEvent,
) -> TourneyLogEntry:
    return _serialize_tourney_event(event, 'tourney-paused')


def deserialize_tourney_paused_event(
    log_entry: TourneyLogEntry,
) -> TourneyPausedEvent:
    return TourneyPausedEvent(
        occurred_at=log_entry.occurred_at,
        initiator=log_entry.initiator,
        tourney=log_entry.tourney,
    )


def serialize_tourney_continued_event(
    event: TourneyContinuedEvent,
) -> TourneyLogEntry:
    return _serialize_tourney_event(event, 'tourney-continued')


def deserialize_tourney_continued_event(
    log_entry: TourneyLogEntry,
) -> TourneyContinuedEvent:
    return TourneyContinuedEvent(
        occurred_at=log_entry.occurred_at,
        initiator=log_entry.initiator,
        tourney=log_entry.tourney,
    )


def serialize_tourney_canceled_event(
    event: TourneyCanceledEvent,
) -> TourneyLogEntry:
    return _serialize_tourney_event(event, 'tourney-canceled')


def deserialize_tourney_canceled_event(
    log_entry: TourneyLogEntry,
) -> TourneyCanceledEvent:
    return TourneyCanceledEvent(
        occurred_at=log_entry.occurred_at,
        initiator=log_entry.initiator,
        tourney=log_entry.tourney,
    )


def serialize_tourney_finished_event(
    event: TourneyFinishedEvent,
) -> TourneyLogEntry:
    return _serialize_tourney_event(event, 'tourney-finished')


def deserialize_tourney_finished_event(
    log_entry: TourneyLogEntry,
) -> TourneyFinishedEvent:
    return TourneyFinishedEvent(
        occurred_at=log_entry.occurred_at,
        initiator=log_entry.initiator,
        tourney=log_entry.tourney,
    )


def _serialize_tourney_event(
    event: TourneyEvent, event_type: str
) -> TourneyLogEntry:
    entry_id = generate_uuid7()

    return TourneyLogEntry(
        id=entry_id,
        occurred_at=event.occurred_at,
        event_type=event_type,
        tourney=event.tourney,
        initiator=event.initiator,
        data={},
    )
