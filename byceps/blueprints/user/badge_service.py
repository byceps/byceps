# -*- coding: utf-8 -*-

"""
byceps.blueprints.user.service.badge_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...database import db

from .models.badge import Badge


def create_badge(label, image_filename, *, description=None):
    """Introduce a new badge."""
    badge = Badge(label, image_filename, description=description)

    db.session.add(badge)
    db.session.commit()

    return badge


def award_badge_to_user(badge, user):
    """Award the badge to the user."""
    badge.recipients.add(user)
    db.session.commit()
