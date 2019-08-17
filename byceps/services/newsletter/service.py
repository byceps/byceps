"""
byceps.services.newsletter.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from collections import Counter
from operator import itemgetter
from typing import Any, Dict, Iterable, Iterator, Optional, Sequence, Set, \
    Tuple, Union

from ...database import BaseQuery, db
from ...typing import UserID

from ..user.models.user import User as DbUser
from ..user.transfer.models import User

from .models import List as DbList, Subscriber, Subscription
from .transfer.models import List, ListID
from .types import SubscriptionState


def find_list(list_id: ListID) -> Optional[List]:
    """Return the list with that ID, or `None` if not found."""
    list_ = DbList.query.get(list_id)

    if list_ is None:
        return None

    return _db_entity_to_list(list_)


def get_all_lists() -> Sequence[List]:
    """Return all lists."""
    lists = DbList.query.all()

    return [_db_entity_to_list(list_) for list_ in lists]


def count_subscribers_for_list(list_id: ListID) -> int:
    """Return the number of users that are currently subscribed to that list."""
    return _build_query_for_current_subscribers(list_id).count()


def get_subscribers(list_id: ListID) -> Iterable[Subscriber]:
    """Yield screen name and email address of the enabled users that
    are currently subscribed to the list.
    """
    subscriber_id_rows = _build_query_for_current_subscribers(list_id).all()

    subscriber_ids = set(map(itemgetter(0), subscriber_id_rows))

    return _get_subscriber_details(subscriber_ids)


def _build_query_for_current_subscribers(list_id: ListID) -> BaseQuery:
    """Build a query to return the most recent subscription state
    (grouped by user and list).

    The generated SQL should be equivalent to this:

        SELECT
          nso.user_id
        FROM newsletter_subscriptions AS nso
          JOIN (
            SELECT
              user_id,
              list_id,
              MAX(expressed_at) AS latest_expressed_at
            FROM newsletter_subscriptions
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
            Subscription.user_id
        ) \
        .join(subquery, db.and_(
            Subscription.user_id == subquery.c.user_id,
            Subscription.list_id == subquery.c.list_id,
            Subscription.expressed_at == subquery.c.latest_expressed_at
        )) \
        .filter(Subscription._state == SubscriptionState.requested.name) \
        .filter(Subscription.list_id == list_id)


def _get_subscriber_details(user_ids: Set[UserID]) -> Iterator[Subscriber]:
    """Yield screen name and email address of each user (if enabled)."""
    if not user_ids:
        return []

    rows = db.session \
        .query(
            DbUser.screen_name,
            DbUser.email_address,
        ) \
        .filter(DbUser.id.in_(user_ids)) \
        .filter_by(enabled=True) \
        .filter_by(suspended=False) \
        .filter_by(deleted=False) \
        .all()

    for row in rows:
        yield Subscriber(row.screen_name, row.email_address)


def count_subscriptions_by_state(list_id: ListID
                                ) -> Dict[Union[SubscriptionState, str], int]:
    """Return the totals for each state as well as an overall total."""
    rows = _build_query_for_current_state(list_id) \
        .all()

    totals = {state: 0 for state in SubscriptionState}

    for state_name, count in rows:
        state = SubscriptionState[state_name]
        totals[state] = count

    totals['total'] = sum(totals.values())

    return totals


def _build_query_for_current_state(list_id: ListID) -> BaseQuery:
    """Build a query to return the number of currently requested and
    declined subscription states for that list.

    The generated SQL should be equivalent to this:

        SELECT
          nso.state,
          COUNT(nso.state)
        FROM newsletter_subscriptions AS nso
          JOIN (
            SELECT
              user_id,
              list_id,
              MAX(expressed_at) AS latest_expressed_at
            FROM newsletter_subscriptions
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
            Subscription._state,
            db.func.count(Subscription._state),
        ) \
        .join(subquery, db.and_(
            Subscription.user_id == subquery.c.user_id,
            Subscription.list_id == subquery.c.list_id,
            Subscription.expressed_at == subquery.c.latest_expressed_at
        )) \
        .filter_by(list_id=list_id) \
        .group_by(
            Subscription.list_id,
            Subscription._state,
        )


def _build_query_for_latest_expressed_at() -> BaseQuery:
    """Build a query to return the most recent time the subscription
    state was set (grouped by user and list).

    The generated SQL should be equivalent to this:

        SELECT user_id, list_id, MAX(expressed_at) AS latest_expressed_at
        FROM newsletter_subscriptions
        GROUP BY user_id, list_id
    """
    return db.session \
        .query(
            Subscription.user_id,
            Subscription.list_id,
            db.func.max(Subscription.expressed_at).label('latest_expressed_at')
        ) \
        .group_by(
            Subscription.user_id,
            Subscription.list_id
        )


def get_subscription_state(user_id: UserID, list_id: ListID
                          ) -> SubscriptionState:
    """Return the user's current subscription state for that list."""
    current_subscription = Subscription.query \
        .filter_by(user_id=user_id) \
        .filter_by(list_id=list_id) \
        .order_by(Subscription.expressed_at.desc()) \
        .first()

    if current_subscription is None:
        return SubscriptionState.declined

    return current_subscription.state


def get_subscription_updates_for_user(user_id: UserID
                                     ) -> Sequence[Subscription]:
    """Return subscription updates made by the user, for any list."""
    return Subscription.query \
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
