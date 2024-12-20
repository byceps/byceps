"""
byceps.services.newsletter.newsletter_command_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert

from byceps.database import db
from byceps.events.newsletter import (
    SubscribedToNewsletterEvent,
    UnsubscribedFromNewsletterEvent,
)
from byceps.services.user.models.user import User
from byceps.util.result import Err, Ok, Result

from . import newsletter_domain_service, newsletter_service
from .dbmodels import DbList, DbSubscription, DbSubscriptionUpdate
from .errors import UnknownListIdError
from .models import List, ListID, SubscriptionUpdate


def create_list(list_id: ListID, title: str) -> List:
    """Create a list."""
    db_list = DbList(list_id, title)

    db.session.add(db_list)
    db.session.commit()

    return newsletter_service._db_entity_to_list(db_list)


def delete_list(list_id: ListID) -> None:
    """Delete a list."""
    db.session.execute(delete(DbList).filter_by(id=list_id))
    db.session.commit()


def subscribe_user_to_list(
    user: User, list_: List, expressed_at: datetime
) -> Result[
    tuple[SubscriptionUpdate, SubscribedToNewsletterEvent], UnknownListIdError
]:
    """Subscribe the user to that list."""
    subscription_update, event = (
        newsletter_domain_service.subscribe_user_to_list(
            user, list_, expressed_at
        )
    )

    update_subscription_state_result = _update_subscription_state(
        subscription_update
    )
    if update_subscription_state_result.is_err():
        return Err(update_subscription_state_result.unwrap_err())

    table = DbSubscription.__table__
    query = (
        insert(table)
        .values(
            {
                'user_id': str(user.id),
                'list_id': str(list_.id),
            }
        )
        .on_conflict_do_nothing(constraint=table.primary_key)
    )
    db.session.execute(query)
    db.session.commit()

    return Ok((subscription_update, event))


def unsubscribe(
    user: User, list_: List, expressed_at: datetime
) -> Result[
    tuple[SubscriptionUpdate, UnsubscribedFromNewsletterEvent],
    UnknownListIdError,
]:
    """Unsubscribe the user from that list."""
    subscription_update, event = newsletter_domain_service.unsubscribe(
        user, list_, expressed_at
    )

    update_subscription_state_result = _update_subscription_state(
        subscription_update
    )
    if update_subscription_state_result.is_err():
        return Err(update_subscription_state_result.unwrap_err())

    db.session.execute(
        delete(DbSubscription)
        .where(DbSubscription.user_id == user.id)
        .where(DbSubscription.list_id == list_.id)
    )
    db.session.commit()

    return Ok((subscription_update, event))


def _update_subscription_state(
    subscription_update: SubscriptionUpdate,
) -> Result[None, UnknownListIdError]:
    """Update the user's subscription state for that list."""
    list_result = newsletter_service.get_list(subscription_update.list_id)
    if list_result.is_err():
        return Err(list_result.unwrap_err())

    db_subscription_update = DbSubscriptionUpdate(
        subscription_update.user_id,
        subscription_update.list_id,
        subscription_update.expressed_at,
        subscription_update.state,
    )

    db.session.add(db_subscription_update)

    return Ok(None)
