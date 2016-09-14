# -*- coding: utf-8 -*-

"""
byceps.blueprints.newsletter.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...database import db

from .models import Subscription, SubscriptionState


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
