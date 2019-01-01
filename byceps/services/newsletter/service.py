"""
byceps.services.newsletter.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from collections import Counter
from operator import itemgetter
from typing import Any, Dict, Iterable, Iterator, Sequence, Set, Tuple, Union

from ...database import BaseQuery, db
from ...typing import BrandID, UserID

from ..user.models.user import User as DbUser
from ..user.transfer.models import User

from .models import Subscriber, Subscription
from .types import SubscriptionState


def count_subscribers_for_brand(brand_id: BrandID) -> int:
    """Return the number of users that are currently subscribed to that
    brand's newsletter.
    """
    return _build_query_for_current_subscribers(brand_id).count()


def get_subscribers(brand_id: BrandID) -> Iterable[Subscriber]:
    """Yield screen name and email address of the enabled users that
    are currently subscribed for the brand.
    """
    subscriber_id_rows = _build_query_for_current_subscribers(brand_id).all()

    subscriber_ids = set(map(itemgetter(0), subscriber_id_rows))

    return _get_subscriber_details(subscriber_ids)


def _build_query_for_current_subscribers(brand_id: BrandID) -> BaseQuery:
    """Build a query to return the most recent subscription state
    (grouped by user and brand).

    The generated SQL should be equivalent to this:

        SELECT
          nso.user_id
        FROM newsletter_subscriptions AS nso
          JOIN (
            SELECT
              user_id,
              brand_id,
              MAX(expressed_at) AS latest_expressed_at
            FROM newsletter_subscriptions
            GROUP BY
              user_id,
              brand_id
          ) AS nsi
            ON nso.user_id = nsi.user_id
              AND nso.brand_id = nsi.brand_id
              AND nso.expressed_at = nsi.latest_expressed_at
        WHERE nso.state = 'requested'
          AND nso.brand_id = <brand_id>
    """
    subquery = _build_query_for_latest_expressed_at().subquery()

    return db.session \
        .query(
            Subscription.user_id
        ) \
        .join(subquery, db.and_(
            Subscription.user_id == subquery.c.user_id,
            Subscription.brand_id == subquery.c.brand_id,
            Subscription.expressed_at == subquery.c.latest_expressed_at
        )) \
        .filter(Subscription._state == SubscriptionState.requested.name) \
        .filter(Subscription.brand_id == brand_id)


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


def count_subscriptions_by_state(brand_id: BrandID
                                ) -> Dict[Union[SubscriptionState, str], int]:
    """Return the totals for each state as well as an overall total."""
    rows = _build_query_for_current_state(brand_id) \
        .all()

    totals = {state: 0 for state in SubscriptionState}

    for state_name, count in rows:
        state = SubscriptionState[state_name]
        totals[state] = count

    totals['total'] = sum(totals.values())

    return totals


def _build_query_for_current_state(brand_id: BrandID) -> BaseQuery:
    """Build a query to return the number of currently requested and
    declined subscription states for that brand.

    The generated SQL should be equivalent to this:

        SELECT
          nso.state,
          COUNT(nso.state)
        FROM newsletter_subscriptions AS nso
          JOIN (
            SELECT
              user_id,
              brand_id,
              MAX(expressed_at) AS latest_expressed_at
            FROM newsletter_subscriptions
            GROUP BY
              user_id,
              brand_id
          ) AS nsi
            ON nso.user_id = nsi.user_id
              AND nso.brand_id = nsi.brand_id
              AND nso.expressed_at = nsi.latest_expressed_at
        WHERE brand_id = {brand_id}
        GROUP BY
          brand_id,
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
            Subscription.brand_id == subquery.c.brand_id,
            Subscription.expressed_at == subquery.c.latest_expressed_at
        )) \
        .filter_by(brand_id=brand_id) \
        .group_by(
            Subscription.brand_id,
            Subscription._state,
        )


def _build_query_for_latest_expressed_at() -> BaseQuery:
    """Build a query to return the most recent time the subscription
    state was set (grouped by user and brand).

    The generated SQL should be equivalent to this:

        SELECT user_id, brand_id, MAX(expressed_at) AS latest_expressed_at
        FROM newsletter_subscriptions
        GROUP BY user_id, brand_id
    """
    return db.session \
        .query(
            Subscription.user_id,
            Subscription.brand_id,
            db.func.max(Subscription.expressed_at).label('latest_expressed_at')
        ) \
        .group_by(
            Subscription.user_id,
            Subscription.brand_id
        )


def get_subscription_state(user_id: UserID, brand_id: BrandID
                          ) -> SubscriptionState:
    """Return the user's current subscription state for that brand."""
    current_subscription = Subscription.query \
        .filter_by(user_id=user_id) \
        .filter_by(brand_id=brand_id) \
        .order_by(Subscription.expressed_at.desc()) \
        .first()

    if current_subscription is None:
        return SubscriptionState.declined

    return current_subscription.state


def get_subscription_updates_for_user(user_id: UserID
                                     ) -> Sequence[Subscription]:
    """Return subscription updates made by the user, for any brand."""
    return Subscription.query \
        .filter_by(user_id=user_id) \
        .all()


def is_subscribed(user_id: UserID, brand_id: BrandID) -> bool:
    """Return if the user is subscribed to the brand's newsletter or not."""
    subscription_state = get_subscription_state(user_id, brand_id)
    return subscription_state == SubscriptionState.requested
