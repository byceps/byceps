"""
byceps.services.newsletter.newsletter_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from collections.abc import Iterator, Sequence

from sqlalchemy import select

from byceps.database import db
from byceps.services.user.dbmodels.user import DbUser
from byceps.typing import UserID

from .dbmodels import DbList, DbSubscription, DbSubscriptionUpdate
from .models import List, ListID, Subscriber


def find_list(list_id: ListID) -> List | None:
    """Return the list with that ID, or `None` if not found."""
    db_list = db.session.get(DbList, list_id)

    if db_list is None:
        return None

    return _db_entity_to_list(db_list)


def get_all_lists() -> list[List]:
    """Return all lists."""
    db_lists = db.session.scalars(select(DbList)).all()

    return [_db_entity_to_list(db_list) for db_list in db_lists]


def count_subscribers(list_id: ListID) -> int:
    """Return the number of users that are currently subscribed to that list."""
    return db.session.scalar(
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


def get_subscribers(list_id: ListID) -> Iterator[Subscriber]:
    """Yield screen name and email address of the users that are
    currently subscribed to the list.

    This excludes user accounts that are
    - not initialized,
    - have no or an unverified email address,
    - are suspended, or
    - have been deleted.
    """
    rows = db.session.execute(
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
    ).all()

    for row in rows:
        yield Subscriber(
            screen_name=row.screen_name,
            email_address=row.email_address,
        )


def get_subscription_updates_for_user(
    user_id: UserID,
) -> Sequence[DbSubscriptionUpdate]:
    """Return subscription updates made by the user, for any list."""
    return db.session.scalars(
        select(DbSubscriptionUpdate).filter_by(user_id=user_id)
    ).all()


def is_subscribed(user_id: UserID, list_id: ListID) -> bool:
    """Return if the user is subscribed to the list or not."""
    return db.session.scalar(
        select(
            db.exists()
            .where(DbSubscription.user_id == user_id)
            .where(DbSubscription.list_id == list_id)
        )
    )


def _db_entity_to_list(db_list: DbList) -> List:
    return List(
        id=db_list.id,
        title=db_list.title,
    )
