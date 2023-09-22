"""
byceps.services.newsletter.newsletter_command_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert

from byceps.database import db
from byceps.services.user.models.user import User
from byceps.util.result import Err, Ok, Result

from . import newsletter_service
from .dbmodels import DbList, DbSubscription, DbSubscriptionUpdate
from .errors import UnknownListIdError
from .models import List, ListID, SubscriptionState, SubscriptionUpdate


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


def subscribe(
    user: User, list_: List, expressed_at: datetime
) -> Result[SubscriptionUpdate, UnknownListIdError]:
    """Subscribe the user to that list."""
    update_subscription_state_result = _update_subscription_state(
        user, list_, expressed_at, SubscriptionState.requested
    )
    if update_subscription_state_result.is_err():
        return Err(update_subscription_state_result.unwrap_err())

    subscription_update = update_subscription_state_result.unwrap()

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

    return Ok(subscription_update)


def unsubscribe(
    user: User, list_: List, expressed_at: datetime
) -> Result[SubscriptionUpdate, UnknownListIdError]:
    """Unsubscribe the user from that list."""
    update_subscription_state_result = _update_subscription_state(
        user, list_, expressed_at, SubscriptionState.declined
    )
    if update_subscription_state_result.is_err():
        return Err(update_subscription_state_result.unwrap_err())

    subscription_update = update_subscription_state_result.unwrap()

    db.session.execute(
        delete(DbSubscription)
        .where(DbSubscription.user_id == user.id)
        .where(DbSubscription.list_id == list_.id)
    )
    db.session.commit()

    return Ok(subscription_update)


def _update_subscription_state(
    user: User,
    list_: List,
    expressed_at: datetime,
    state: SubscriptionState,
) -> Result[SubscriptionUpdate, UnknownListIdError]:
    """Update the user's subscription state for that list."""
    list_result = newsletter_service.get_list(list_.id)
    if list_result.is_err():
        return Err(list_result.unwrap_err())

    db_subscription_update = DbSubscriptionUpdate(
        user.id, list_.id, expressed_at, state
    )

    db.session.add(db_subscription_update)

    subscription_update = SubscriptionUpdate(
        user_id=user.id,
        list_id=list_.id,
        expressed_at=expressed_at,
        state=state,
    )

    return Ok(subscription_update)
