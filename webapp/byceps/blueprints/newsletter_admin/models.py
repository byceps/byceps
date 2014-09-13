# -*- coding: utf-8 -*-

"""
byceps.blueprints.newsletter_admin.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from collections import Counter
from operator import itemgetter

from ...database import db

from ..newsletter.models import NewsletterSubscription, SubscriptionState
from ..user.models import User


def get_subscriptions_for_brand(brand):
    """Return subscriptions as (user, state) pairs for the brand."""
    subscriptions = build_query_for_current_state() \
        .filter_by(brand_id=brand.id) \
        .all()

    user_ids = frozenset(map(itemgetter(0), subscriptions))
    users = User.query.filter(User.id.in_(user_ids))
    users_by_id = {user.id: user for user in users}

    for user_id, brand_id, state_name in subscriptions:
        state = SubscriptionState[state_name]
        yield users_by_id[user_id], state


def build_query_for_current_state():
    """Build a query to return the most recent subscription state
    (grouped by user and brand).

    The generated SQL should be equivalent to this:

        SELECT
          nso.user_id,
          nso.brand_id,
          nso.state
        FROM newsletter_subscriptions nso
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
    subquery = build_query_for_latest_expressed_at().subquery()
    return db.session \
        .query(
            NewsletterSubscription.user_id,
            NewsletterSubscription.brand_id,
            NewsletterSubscription._state
        ) \
        .join(subquery, db.and_(
            NewsletterSubscription.user_id == subquery.c.user_id,
            NewsletterSubscription.brand_id == subquery.c.brand_id,
            NewsletterSubscription.expressed_at == subquery.c.latest_expressed_at
        ));


def build_query_for_latest_expressed_at():
    """Build a query to return the most recent time the subscription
    state was set (grouped by user and brand).

    The generated SQL should be equivalent to this:

        SELECT user_id, brand_id, MAX(expressed_at) AS latest_expressed_at
        FROM newsletter_subscriptions
        GROUP BY user_id, brand_id
    """
    return db.session \
        .query(
            NewsletterSubscription.user_id,
            NewsletterSubscription.brand_id,
            db.func.max(NewsletterSubscription.expressed_at) \
                .label('latest_expressed_at')
        ) \
        .group_by(
            NewsletterSubscription.user_id,
            NewsletterSubscription.brand_id
        )


def count_subscriptions_by_state(subscriptions):
    """Return the totals for each state as well as an overall total."""
    counter = Counter(state for _, state in subscriptions)

    totals = {}
    for state in SubscriptionState:
        totals[state] = counter.get(state, 0)
    totals['total'] = sum(totals.values())

    return totals
