"""
byceps.services.newsletter.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from operator import itemgetter
from typing import Iterable, Iterator, Optional, Sequence, Union

from ...database import db, Query
from ...typing import UserID

from ..user.dbmodels.user import User as DbUser

from .dbmodels import (
    List as DbList,
    Subscriber,
    SubscriptionUpdate as DbSubscriptionUpdate,
)
from .transfer.models import List, ListID
from .types import SubscriptionState


def find_list(list_id: ListID) -> Optional[List]:
    """Return the list with that ID, or `None` if not found."""
    list_ = db.session.get(DbList, list_id)

    if list_ is None:
        return None

    return _db_entity_to_list(list_)


def get_all_lists() -> Sequence[List]:
    """Return all lists."""
    lists = db.session.query(DbList).all()

    return [_db_entity_to_list(list_) for list_ in lists]


def count_subscribers_for_list(list_id: ListID) -> int:
    """Return the number of users that are currently subscribed to that list."""
    return _build_query_for_current_subscribers(list_id).count()


def get_subscribers(list_id: ListID) -> Iterable[Subscriber]:
    """Yield screen name and email address of the initialized users that
    are currently subscribed to the list.
    """
    subscriber_id_rows = _build_query_for_current_subscribers(list_id).all()

    subscriber_ids = set(map(itemgetter(0), subscriber_id_rows))

    return _get_subscriber_details(subscriber_ids)


def _build_query_for_current_subscribers(list_id: ListID) -> Query:
    """Build a query to return the most recent subscription state
    (grouped by user and list).

    The generated SQL should be equivalent to this:

        SELECT
          nso.user_id
        FROM newsletter_subscription_updates AS nso
          JOIN (
            SELECT
              user_id,
              list_id,
              MAX(expressed_at) AS latest_expressed_at
            FROM newsletter_subscription_updates
            GROUP BY
              user_id,
              list_id
          ) AS nsi
            ON nso.user_id = nsi.user_id
              AND nso.list_id = nsi.list_id
              AND nso.expressed_at = nsi.latest_expressed_at
        WHERE nso.state = 'requested'
          AND nso.list_id = <list_id>
    """
    subquery = _build_query_for_latest_expressed_at().subquery()

    return db.session \
        .query(
            DbSubscriptionUpdate.user_id
        ) \
        .join(subquery, db.and_(
            DbSubscriptionUpdate.user_id == subquery.c.user_id,
            DbSubscriptionUpdate.list_id == subquery.c.list_id,
            DbSubscriptionUpdate.expressed_at == subquery.c.latest_expressed_at
        )) \
        .filter(DbSubscriptionUpdate._state == SubscriptionState.requested.name) \
        .filter(DbSubscriptionUpdate.list_id == list_id)


def _get_subscriber_details(user_ids: set[UserID]) -> Iterator[Subscriber]:
    """Yield screen name and email address of each eligible user."""
    if not user_ids:
        return []

    rows = db.session \
        .query(
            DbUser.screen_name,
            DbUser.email_address,
        ) \
        .filter(DbUser.id.in_(user_ids)) \
        .filter(DbUser.email_address != None) \
        .filter_by(initialized=True) \
        .filter_by(email_address_verified=True) \
        .filter_by(suspended=False) \
        .filter_by(deleted=False) \
        .all()

    for row in rows:
        yield Subscriber(row.screen_name, row.email_address)


def count_subscriptions_by_state(
    list_id: ListID,
) -> dict[Union[SubscriptionState, str], int]:
    """Return the totals for each state as well as an overall total."""
    rows = _build_query_for_current_state(list_id) \
        .all()

    totals: dict[Union[SubscriptionState, str], int] = {
        state: 0 for state in SubscriptionState
    }

    for state_name, count in rows:
        state = SubscriptionState[state_name]
        totals[state] = count

    totals['total'] = sum(totals.values())

    return totals


def _build_query_for_current_state(list_id: ListID) -> Query:
    """Build a query to return the number of currently requested and
    declined subscription states for that list.

    The generated SQL should be equivalent to this:

        SELECT
          nso.state,
          COUNT(nso.state)
        FROM newsletter_subscription_updates AS nso
          JOIN (
            SELECT
              user_id,
              list_id,
              MAX(expressed_at) AS latest_expressed_at
            FROM newsletter_subscription_updates
            GROUP BY
              user_id,
              list_id
          ) AS nsi
            ON nso.user_id = nsi.user_id
              AND nso.list_id = nsi.list_id
              AND nso.expressed_at = nsi.latest_expressed_at
        WHERE list_id = {list_id}
        GROUP BY
          list_id,
          state
    """
    subquery = _build_query_for_latest_expressed_at().subquery()

    return db.session \
        .query(
            DbSubscriptionUpdate._state,
            db.func.count(DbSubscriptionUpdate._state),
        ) \
        .join(subquery, db.and_(
            DbSubscriptionUpdate.user_id == subquery.c.user_id,
            DbSubscriptionUpdate.list_id == subquery.c.list_id,
            DbSubscriptionUpdate.expressed_at == subquery.c.latest_expressed_at
        )) \
        .filter_by(list_id=list_id) \
        .group_by(
            DbSubscriptionUpdate.list_id,
            DbSubscriptionUpdate._state,
        )


def _build_query_for_latest_expressed_at() -> Query:
    """Build a query to return the most recent time the subscription
    state was set (grouped by user and list).

    The generated SQL should be equivalent to this:

        SELECT user_id, list_id, MAX(expressed_at) AS latest_expressed_at
        FROM newsletter_subscription_updates
        GROUP BY user_id, list_id
    """
    return db.session \
        .query(
            DbSubscriptionUpdate.user_id,
            DbSubscriptionUpdate.list_id,
            db.func.max(DbSubscriptionUpdate.expressed_at)
                .label('latest_expressed_at')
        ) \
        .group_by(
            DbSubscriptionUpdate.user_id,
            DbSubscriptionUpdate.list_id
        )


def get_subscription_state(
    user_id: UserID, list_id: ListID
) -> SubscriptionState:
    """Return the user's current subscription state for that list."""
    current_subscription = db.session \
        .query(DbSubscriptionUpdate) \
        .filter_by(user_id=user_id) \
        .filter_by(list_id=list_id) \
        .order_by(DbSubscriptionUpdate.expressed_at.desc()) \
        .first()

    if current_subscription is None:
        return SubscriptionState.declined

    return current_subscription.state


def get_subscription_updates_for_user(
    user_id: UserID,
) -> Sequence[DbSubscriptionUpdate]:
    """Return subscription updates made by the user, for any list."""
    return db.session \
        .query(DbSubscriptionUpdate) \
        .filter_by(user_id=user_id) \
        .all()


def is_subscribed(user_id: UserID, list_id: ListID) -> bool:
    """Return if the user is subscribed to the list or not."""
    subscription_state = get_subscription_state(user_id, list_id)
    return subscription_state == SubscriptionState.requested


def _db_entity_to_list(list_: DbList) -> List:
    return List(
        list_.id,
        list_.title,
    )
