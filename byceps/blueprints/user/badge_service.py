# -*- coding: utf-8 -*-

"""
byceps.blueprints.user.service.badge_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...database import db


def award_badge_to_user(badge, user):
    """Award the badge to the user."""
    badge.recipients.add(user)
    db.session.commit()
