# -*- coding: utf-8 -*-

"""
byceps.blueprints.newsletter.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...database import db

from .models import Subscription, SubscriptionState


def get_subscription_state(user, brand):
    """Return the user's current subscription state for that brand."""
    current_subscription = Subscription.query \
        .filter_by(user=user) \
        .filter_by(brand=brand) \
        .order_by(Subscription.expressed_at.desc()) \
        .first()

    if current_subscription is None:
        return SubscriptionState.declined

    return current_subscription.state


def subscribe(user, brand):
    """Subscribe the user to that brand's newsletter."""
    _update_subscription_state(user, brand, SubscriptionState.requested)


def unsubscribe(user, brand):
    """Unsubscribe the user from that brand's newsletter."""
    _update_subscription_state(user, brand, SubscriptionState.declined)


def _update_subscription_state(user, brand, state):
    """Update the user's subscription state for that brand."""
    subscription = Subscription(user, brand, state)
    db.session.add(subscription)
    db.session.commit()
