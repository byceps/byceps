"""
byceps.services.newsletter.newsletter_repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Sequence

from sqlalchemy import select, delete
from sqlalchemy.dialects.postgresql import insert

from byceps.database import db
from byceps.services.user.dbmodels.user import DbUser
from byceps.services.user.models.user import UserID
from byceps.util.result import Err, Ok, Result

from .dbmodels import DbList, DbSubscription, DbSubscriptionUpdate
from .errors import UnknownListIdError
from .models import ListID, SubscriptionUpdate


def create_list(list_id: ListID, title: str) -> DbList:
    """Create a list."""
    db_list = DbList(list_id, title)

    db.session.add(db_list)
    db.session.commit()

    return db_list


def delete_list(list_id: ListID) -> None:
    """Delete a list."""
    db.session.execute(delete(DbList).filter_by(id=list_id))
    db.session.commit()


def find_list(list_id: ListID) -> DbList | None:
    """Return the list with that ID, or `None` if not found."""
    return db.session.get(DbList, list_id)


def get_all_lists() -> Sequence[DbList]:
    """Return all lists."""
    return db.session.scalars(select(DbList)).all()


def subscribe_user_to_list(
    subscription_update: SubscriptionUpdate,
) -> Result[None, UnknownListIdError]:
    """Subscribe the user to that list."""
    match _update_subscription_state(subscription_update):
        case Err(e):
            return Err(e)

    table = DbSubscription.__table__
    query = (
        insert(table)
        .values(
            {
                'user_id': str(subscription_update.user_id),
                'list_id': str(subscription_update.list_id),
            }
        )
        .on_conflict_do_nothing(constraint=table.primary_key)
    )
    db.session.execute(query)
    db.session.commit()

    return Ok(None)


def unsubscribe_user_from_list(
    subscription_update: SubscriptionUpdate,
) -> Result[None, UnknownListIdError]:
    """Unsubscribe the user from that list."""
    match _update_subscription_state(subscription_update):
        case Err(e):
            return Err(e)

    db.session.execute(
        delete(DbSubscription)
        .where(DbSubscription.user_id == subscription_update.user_id)
        .where(DbSubscription.list_id == subscription_update.list_id)
    )
    db.session.commit()

    return Ok(None)


def _update_subscription_state(
    subscription_update: SubscriptionUpdate,
) -> Result[None, UnknownListIdError]:
    """Update the user's subscription state for that list."""
    list_id = subscription_update.list_id
    list_ = find_list(list_id)
    if list_ is None:
        return Err(UnknownListIdError(list_id))

    db_subscription_update = DbSubscriptionUpdate(
        subscription_update.user_id,
        subscription_update.list_id,
        subscription_update.expressed_at,
        subscription_update.state,
    )

    db.session.add(db_subscription_update)

    return Ok(None)


def count_subscribers_to_list(list_id: ListID) -> int:
    """Return the number of users that are currently subscribed to that list."""
    return (
        db.session.scalar(
            select(db.func.count())
            .select_from(DbUser)
            .join(DbSubscription)
            .filter(DbSubscription.list_id == list_id)
            .filter(DbUser.email_address.is_not(None))
            .filter(DbUser.initialized == True)  # noqa: E712
            .filter(DbUser.email_address_verified == True)  # noqa: E712
            .filter(DbUser.suspended == False)  # noqa: E712
            .filter(DbUser.deleted == False)  # noqa: E712
        )
        or 0
    )


def get_subscribers_to_list(
    list_id: ListID,
) -> Sequence[tuple[str | None, str]]:
    """Yield screen name and email address of the users that are
    currently subscribed to the list.

    This excludes user accounts that are
    - not initialized,
    - have no or an unverified email address,
    - are suspended, or
    - have been deleted.
    """
    return (
        db.session.execute(
            select(
                DbUser.screen_name,
                DbUser.email_address,
            )
            .join(DbSubscription)
            .filter(DbSubscription.list_id == list_id)
            .filter(DbUser.email_address.is_not(None))
            .filter(DbUser.initialized == True)  # noqa: E712
            .filter(DbUser.email_address_verified == True)  # noqa: E712
            .filter(DbUser.suspended == False)  # noqa: E712
            .filter(DbUser.deleted == False)  # noqa: E712
            .order_by(DbUser.email_address)
        )
        .tuples()
        .all()
    )


def get_subscription_updates_for_user(
    user_id: UserID,
) -> Sequence[DbSubscriptionUpdate]:
    """Return subscription updates made by the user, for any list."""
    return db.session.scalars(
        select(DbSubscriptionUpdate).filter_by(user_id=user_id)
    ).all()


def is_user_subscribed_to_list(user_id: UserID, list_id: ListID) -> bool:
    """Return if the user is subscribed to the list or not."""
    return (
        db.session.scalar(
            select(
                db.exists()
                .where(DbSubscription.user_id == user_id)
                .where(DbSubscription.list_id == list_id)
            )
        )
        or False
    )
