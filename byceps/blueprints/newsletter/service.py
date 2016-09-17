# -*- coding: utf-8 -*-

"""
byceps.blueprints.newsletter.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from collections import Counter
from operator import itemgetter

from ...database import db

from ..user.models.user import User

from .models import Subscription, SubscriptionState


def count_subscribers_for_brand(brand_id):
    """Return the number of users that are currently subscribed to that
    brand's newsletter.
    """
    return _build_query_for_current_subscribers(brand_id).count()


def get_subscribers(brand_id):
    """Return the enabled users that are currently subscribed for the brand."""
    subscribers = _build_query_for_current_subscribers(brand_id).all()

    user_ids = frozenset(map(itemgetter(0), subscribers))
    return _get_users_query(user_ids).filter_by(enabled=True).all()


def _build_query_for_current_subscribers(brand_id):
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


def get_user_subscription_states_for_brand(brand_id):
    """Return subscriptions as (user, state) pairs for the brand."""
    subscription_states = _build_query_for_current_state() \
        .filter_by(brand_id=brand_id) \
        .all()

    user_ids = frozenset(map(itemgetter(0), subscription_states))
    users = _get_users_query(user_ids).all()
    users_by_id = {user.id: user for user in users}

    for user_id, brand_id, state_name in subscription_states:
        state = SubscriptionState[state_name]
        yield users_by_id[user_id], state


def _build_query_for_current_state():
    """Build a query to return the most recent subscription state
    (grouped by user and brand).

    The generated SQL should be equivalent to this:

        SELECT
          nso.user_id,
          nso.brand_id,
          nso.state
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
    """
    subquery = _build_query_for_latest_expressed_at().subquery()

    return db.session \
        .query(
            Subscription.user_id,
            Subscription.brand_id,
            Subscription._state
        ) \
        .join(subquery, db.and_(
            Subscription.user_id == subquery.c.user_id,
            Subscription.brand_id == subquery.c.brand_id,
            Subscription.expressed_at == subquery.c.latest_expressed_at
        ))


def _build_query_for_latest_expressed_at():
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


def _get_users_query(user_ids):
    """Return a query to select the users with the given IDs."""
    return User.query.filter(User.id.in_(user_ids))


def count_subscriptions_by_state(subscriptions):
    """Return the totals for each state as well as an overall total."""
    counter = Counter(state for _, state in subscriptions)

    totals = {}
    for state in SubscriptionState:
        totals[state] = counter.get(state, 0)
    totals['total'] = sum(totals.values())

    return totals


def get_subscription_state(user_id, brand_id):
    """Return the user's current subscription state for that brand."""
    current_subscription = Subscription.query \
        .filter_by(user_id=user_id) \
        .filter_by(brand_id=brand_id) \
        .order_by(Subscription.expressed_at.desc()) \
        .first()

    if current_subscription is None:
        return SubscriptionState.declined

    return current_subscription.state


def is_subscribed(user_id, brand_id):
    """Return if the user is subscribed to the brand's newsletter or not."""
    subscription_state = get_subscription_state(user_id, brand_id)
    return subscription_state == SubscriptionState.requested


def subscribe(user_id, brand_id):
    """Subscribe the user to that brand's newsletter."""
    _update_subscription_state(user_id, brand_id, SubscriptionState.requested)


def unsubscribe(user_id, brand_id):
    """Unsubscribe the user from that brand's newsletter."""
    _update_subscription_state(user_id, brand_id, SubscriptionState.declined)


def _update_subscription_state(user_id, brand_id, state):
    """Update the user's subscription state for that brand."""
    subscription = Subscription(user_id, brand_id, state)

    db.session.add(subscription)
    db.session.commit()
