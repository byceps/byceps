"""
byceps.services.user.log.user_log_serialization_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.services.user.events import (
    UserAccountDeletedEvent,
    UserAccountSuspendedEvent,
    UserAccountUnsuspendedEvent,
    UserDetailsUpdatedEvent,
    UserEvent,
    UserScreenNameChangedEvent,
)

from . import user_log_domain_service
from .models import UserLogEntry, UserLogEntryData


def serialize_account_suspended_event(
    event: UserAccountSuspendedEvent,
) -> UserLogEntry:
    return _serialize_user_event(
        event,
        'user-suspended',
        {
            'reason': event.reason,
        },
    )


def serialize_account_unsuspended_event(
    event: UserAccountUnsuspendedEvent,
) -> UserLogEntry:
    return _serialize_user_event(
        event,
        'user-unsuspended',
        {
            'reason': event.reason,
        },
    )


def serialize_account_deleted_event(
    event: UserAccountDeletedEvent,
) -> UserLogEntry:
    return _serialize_user_event(
        event,
        'user-deleted',
        {
            'reason': event.reason,
        },
    )


def serialize_screen_name_changed_event(
    event: UserScreenNameChangedEvent,
) -> UserLogEntry:
    data = {
        'old_screen_name': event.old_screen_name,
        'new_screen_name': event.new_screen_name,
    }

    if event.reason:
        data['reason'] = event.reason

    return _serialize_user_event(event, 'user-screen-name-changed', data)


def serialize_details_updated_event(
    event: UserDetailsUpdatedEvent,
) -> UserLogEntry:
    return _serialize_user_event(
        event,
        'user-details-updated',
        {
            'fields': {
                name: {'old': difference.old, 'new': difference.new}
                for name, difference in event.fields.items()
            },
        },
    )


def _serialize_user_event(
    event: UserEvent,
    event_type: str,
    data: UserLogEntryData | None = None,
) -> UserLogEntry:
    if data is None:
        data = {}

    return user_log_domain_service.build_entry(
        event_type,
        event.user,
        data,
        occurred_at=event.occurred_at,
        initiator=event.initiator,
    )
