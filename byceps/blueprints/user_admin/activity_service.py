# -*- coding: utf-8 -*-

"""
byceps.blueprints.user_admin.activity_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from collections import namedtuple
from enum import Enum

from ...services.newsletter import service as newsletter_service


Activity = namedtuple('Activity', ['occured_at', 'type', 'object'])


ActivityType = Enum('ActivityType', [
    'newsletter_subscription_update',
])


def get_newsletter_subscription_updates_for_user(user_id):
    """Yield the user's newsletter subscription updates as activities."""
    updates = newsletter_service.get_subscription_updates_for_user(user_id)

    for update in updates:
        type_ = ActivityType.newsletter_subscription_update

        yield Activity(update.expressed_at, type_, update)


def sort_activities(activities):
    """Sort activities chronologically backwards, in-place."""
    activities.sort(key=lambda a: a.occured_at, reverse=True)
