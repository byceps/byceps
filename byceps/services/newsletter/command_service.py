"""
byceps.services.newsletter.command_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime

from ...database import db
from ...typing import BrandID, UserID

from .models import Subscription
from .types import SubscriptionState


def subscribe(user_id: UserID, brand_id: BrandID, expressed_at: datetime
             ) -> None:
    """Subscribe the user to that brand's newsletter."""
    _update_subscription_state(user_id, brand_id, expressed_at,
                               SubscriptionState.requested)


def unsubscribe(user_id: UserID, brand_id: BrandID, expressed_at: datetime
               ) -> None:
    """Unsubscribe the user from that brand's newsletter."""
    _update_subscription_state(user_id, brand_id, expressed_at,
                               SubscriptionState.declined)


def _update_subscription_state(user_id: UserID, brand_id: BrandID,
                               expressed_at: datetime, state: SubscriptionState
                              ) -> None:
    """Update the user's subscription state for that brand."""
    subscription = Subscription(user_id, brand_id, expressed_at, state)

    db.session.add(subscription)
    db.session.commit()
