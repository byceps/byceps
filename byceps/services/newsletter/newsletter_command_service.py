"""
byceps.services.newsletter.newsletter_command_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

import structlog

from byceps.services.user.models.user import User
from byceps.util.result import Err, Ok, Result

from . import (
    newsletter_domain_service,
    newsletter_repository,
    newsletter_service,
)
from .errors import UnknownListIdError
from .events import (
    SubscribedToNewsletterEvent,
    UnsubscribedFromNewsletterEvent,
)
from .models import List, ListID, SubscriptionUpdate


log = structlog.get_logger()


def create_list(list_id: ListID, title: str) -> List:
    """Create a list."""
    db_list = newsletter_repository.create_list(list_id, title)

    return newsletter_service._db_entity_to_list(db_list)


def delete_list(list_id: ListID) -> None:
    """Delete a list."""
    newsletter_repository.delete_list(list_id)


def subscribe_user_to_list(
    user: User, list_: List, expressed_at: datetime, initiator: User
) -> Result[
    tuple[SubscriptionUpdate, SubscribedToNewsletterEvent], UnknownListIdError
]:
    """Subscribe the user to that list."""
    subscription_update, event = (
        newsletter_domain_service.subscribe_user_to_list(
            user, list_, expressed_at, initiator
        )
    )

    match newsletter_repository.subscribe_user_to_list(subscription_update):
        case Err(e):
            return Err(e)

    return Ok((subscription_update, event))


def unsubscribe_user_from_list(
    user: User, list_: List, expressed_at: datetime, initiator: User
) -> Result[
    tuple[SubscriptionUpdate, UnsubscribedFromNewsletterEvent],
    UnknownListIdError,
]:
    """Unsubscribe the user from that list."""
    subscription_update, event = (
        newsletter_domain_service.unsubscribe_user_from_list(
            user, list_, expressed_at, initiator
        )
    )

    match newsletter_repository.unsubscribe_user_from_list(subscription_update):
        case Err(e):
            return Err(e)

    return Ok((subscription_update, event))


def unsubscribe_user_from_lists(
    user: User, expressed_at: datetime, initiator: User
) -> list[UnsubscribedFromNewsletterEvent]:
    """Unsubscribe the user from the lists they are subscribed to."""
    events = []

    for list_ in newsletter_service.get_lists_user_is_subscribed_to(user.id):
        match unsubscribe_user_from_list(user, list_, expressed_at, initiator):
            case Ok((_, event)):
                events.append(event)
            case Err(e):
                log.error(
                    'Could not unsubscribe user from list.',
                    user_id=user.id,
                    list_id=list_.id,
                    error=e,
                )

    return events
