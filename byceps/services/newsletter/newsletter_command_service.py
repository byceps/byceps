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
from byceps.typing import UserID

from . import newsletter_service
from .dbmodels import DbList, DbSubscription, DbSubscriptionUpdate
from .models import List, ListID
from .types import SubscriptionState


class UnknownListId(Exception):
    pass


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


def subscribe(user_id: UserID, list_id: ListID, expressed_at: datetime) -> None:
    """Subscribe the user to that list."""
    _update_subscription_state(
        user_id, list_id, expressed_at, SubscriptionState.requested
    )

    table = DbSubscription.__table__
    query = (
        insert(table)
        .values(
            {
                'user_id': str(user_id),
                'list_id': str(list_id),
            }
        )
        .on_conflict_do_nothing(constraint=table.primary_key)
    )
    db.session.execute(query)
    db.session.commit()


def unsubscribe(
    user_id: UserID, list_id: ListID, expressed_at: datetime
) -> None:
    """Unsubscribe the user from that list."""
    _update_subscription_state(
        user_id, list_id, expressed_at, SubscriptionState.declined
    )

    db.session.execute(
        delete(DbSubscription)
        .where(DbSubscription.user_id == user_id)
        .where(DbSubscription.list_id == list_id)
    )
    db.session.commit()


def _update_subscription_state(
    user_id: UserID,
    list_id: ListID,
    expressed_at: datetime,
    state: SubscriptionState,
) -> None:
    """Update the user's subscription state for that list."""
    list_ = newsletter_service.find_list(list_id)
    if list_ is None:
        raise UnknownListId(list_id)

    subscription_update = DbSubscriptionUpdate(
        user_id, list_.id, expressed_at, state
    )

    db.session.add(subscription_update)
