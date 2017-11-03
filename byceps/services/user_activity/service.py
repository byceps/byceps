"""
byceps.services.user_activity.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from itertools import chain
from typing import Iterator, List

from ...typing import UserID

from .models import Activity, ActivityType


def get_activities_for_user(user_id: UserID) -> List[Activity]:
    activities = list(chain(
    ))

    _sort_activities(activities)

    return activities


def _sort_activities(activities: List[Activity]) -> None:
    """Sort activities chronologically backwards, in-place."""
    activities.sort(key=lambda a: a.occured_at, reverse=True)
