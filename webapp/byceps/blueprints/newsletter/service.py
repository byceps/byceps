# -*- coding: utf-8 -*-

"""
byceps.blueprints.newsletter.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from .models import Subscription, SubscriptionState


def get_subscription_state(user):
    """Return the user's current subscription state."""
    current_subscription = Subscription.query \
        .filter_by(user=user) \
        .order_by(Subscription.expressed_at.desc()) \
        .first()

    if current_subscription is None:
        return SubscriptionState.declined

    return current_subscription.state
