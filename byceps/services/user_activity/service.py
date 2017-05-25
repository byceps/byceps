"""
byceps.services.user_activity.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from itertools import chain
from typing import Iterator, List

from ...typing import UserID

from ..newsletter import service as newsletter_service
from ..shop.order import service as order_service
from ..terms import service as terms_service
from ..user_avatar import service as avatar_service

from .models import Activity, ActivityType


def get_activities_for_user(user_id: UserID) -> List[Activity]:
    activities = list(chain(
        get_avatar_updates_for_user(user_id),
        get_newsletter_subscription_updates_for_user(user_id),
        get_orders_for_user(user_id),
        get_terms_consents_for_user(user_id),
    ))

    _sort_activities(activities)

    return activities


def get_avatar_updates_for_user(user_id: UserID) -> Iterator[Activity]:
    """Yield the user's avatar updates as activities."""
    avatars = avatar_service.get_avatars_uploaded_by_user(user_id)

    for avatar in avatars:
        type_ = ActivityType.avatar_update

        yield Activity(avatar.created_at, type_, avatar)


def get_newsletter_subscription_updates_for_user(user_id: UserID) \
                                                 -> Iterator[Activity]:
    """Yield the user's newsletter subscription updates as activities."""
    updates = newsletter_service.get_subscription_updates_for_user(user_id)

    for update in updates:
        type_ = ActivityType.newsletter_subscription_update

        yield Activity(update.expressed_at, type_, update)


def get_orders_for_user(user_id: UserID) -> Iterator[Activity]:
    """Yield the orders placed by the user as activities."""
    orders = order_service.get_orders_placed_by_user(user_id)

    for order in orders:
        type_ = ActivityType.order_placement

        yield Activity(order.created_at, type_, order)


def get_terms_consents_for_user(user_id: UserID) -> Iterator[Activity]:
    """Yield the user's consents to terms as activities."""
    consents = terms_service.get_consents_by_user(user_id)

    for consent in consents:
        type_ = ActivityType.terms_consent

        yield Activity(consent.expressed_at, type_, consent)


def _sort_activities(activities: List[Activity]) -> None:
    """Sort activities chronologically backwards, in-place."""
    activities.sort(key=lambda a: a.occured_at, reverse=True)
