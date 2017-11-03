"""
byceps.services.user_activity.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from itertools import chain
from typing import Iterator, List

from ...typing import UserID

from ..shop.order import service as order_service

from .models import Activity, ActivityType


def get_activities_for_user(user_id: UserID) -> List[Activity]:
    activities = list(chain(
        get_orders_for_user(user_id),
    ))

    _sort_activities(activities)

    return activities


def get_orders_for_user(user_id: UserID) -> Iterator[Activity]:
    """Yield the orders placed by the user as activities."""
    orders = order_service.get_orders_placed_by_user(user_id)

    for order in orders:
        type_ = ActivityType.order_placement

        yield Activity(order.created_at, type_, order)


def _sort_activities(activities: List[Activity]) -> None:
    """Sort activities chronologically backwards, in-place."""
    activities.sort(key=lambda a: a.occured_at, reverse=True)
