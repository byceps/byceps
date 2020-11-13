"""
byceps.services.newsletter.command_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from ...database import db
from ...typing import UserID

from .models import List as DbList, SubscriptionUpdate as DbSubscriptionUpdate
from .service import find_list, _db_entity_to_list
from .transfer.models import List, ListID
from .types import SubscriptionState


class UnknownListId(Exception):
    pass


def create_list(list_id: ListID, title: str) -> List:
    """Create a list."""
    list_ = DbList(list_id, title)

    db.session.add(list_)
    db.session.commit()

    return _db_entity_to_list(list_)


def delete_list(list_id: ListID) -> None:
    """Delete a list."""
    db.session.query(DbList) \
        .filter_by(id=list_id) \
        .delete()

    db.session.commit()


def subscribe(user_id: UserID, list_id: ListID, expressed_at: datetime) -> None:
    """Subscribe the user to that list."""
    _update_subscription_state(
        user_id, list_id, expressed_at, SubscriptionState.requested
    )


def unsubscribe(
    user_id: UserID, list_id: ListID, expressed_at: datetime
) -> None:
    """Unsubscribe the user from that list."""
    _update_subscription_state(
        user_id, list_id, expressed_at, SubscriptionState.declined
    )


def _update_subscription_state(
    user_id: UserID,
    list_id: ListID,
    expressed_at: datetime,
    state: SubscriptionState,
) -> None:
    """Update the user's subscription state for that list."""
    list_ = find_list(list_id)
    if list_ is None:
        raise UnknownListId(list_id)

    subscription_update = DbSubscriptionUpdate(
        user_id, list_.id, expressed_at, state
    )

    db.session.add(subscription_update)
    db.session.commit()


def delete_subscription_updates(user_id: UserID, list_id: ListID) -> None:
    """Delete all subscription updates for the user and list."""
    db.session.query(DbSubscriptionUpdate) \
        .filter_by(user_id=user_id, list_id=list_id) \
        .delete()

    db.session.commit()
