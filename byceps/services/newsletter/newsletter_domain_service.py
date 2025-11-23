"""
byceps.services.newsletter.newsletter_domain_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from byceps.services.user.models.user import User

from .events import (
    SubscribedToNewsletterEvent,
    UnsubscribedFromNewsletterEvent,
)
from .models import List, SubscriptionState, SubscriptionUpdate


def subscribe_user_to_list(
    user: User, list_: List, expressed_at: datetime, initiator: User
) -> tuple[SubscriptionUpdate, SubscribedToNewsletterEvent]:
    """Subscribe the user to that list."""
    subscription_update = SubscriptionUpdate(
        user_id=user.id,
        list_id=list_.id,
        expressed_at=expressed_at,
        state=SubscriptionState.requested,
    )

    event = _build_subscribed_to_newsletter_event(
        expressed_at, user, list_, initiator
    )

    return subscription_update, event


def _build_subscribed_to_newsletter_event(
    expressed_at: datetime, user: User, list_: List, initiator: User
) -> SubscribedToNewsletterEvent:
    return SubscribedToNewsletterEvent(
        occurred_at=expressed_at,
        initiator=initiator,
        user=user,
        list_id=list_.id,
        list_title=list_.title,
    )


def unsubscribe_user_from_list(
    user: User, list_: List, expressed_at: datetime, initiator: User
) -> tuple[SubscriptionUpdate, UnsubscribedFromNewsletterEvent]:
    """Unsubscribe the user from that list."""
    subscription_update = SubscriptionUpdate(
        user_id=user.id,
        list_id=list_.id,
        expressed_at=expressed_at,
        state=SubscriptionState.declined,
    )

    event = _build_unsubscribed_from_newsletter_event(
        expressed_at, user, list_, initiator
    )

    return subscription_update, event


def _build_unsubscribed_from_newsletter_event(
    expressed_at: datetime, user: User, list_: List, initiator: User
) -> UnsubscribedFromNewsletterEvent:
    return UnsubscribedFromNewsletterEvent(
        occurred_at=expressed_at,
        initiator=initiator,
        user=user,
        list_id=list_.id,
        list_title=list_.title,
    )
