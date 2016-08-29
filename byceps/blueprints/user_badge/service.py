# -*- coding: utf-8 -*-

"""
byceps.blueprints.user_badge.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...database import db

from .models import Badge


def create_badge(label, image_filename, *, description=None):
    """Introduce a new badge."""
    badge = Badge(label, image_filename, description=description)

    db.session.add(badge)
    db.session.commit()

    return badge


def find_badge(badge_id):
    """Return the badge with that id, or `None` if not found."""
    return Badge.query.get(badge_id)


def get_all_badges():
    """Return all badges."""
    return Badge.query.all()


def award_badge_to_user(badge, user):
    """Award the badge to the user."""
    badge.recipients.add(user)
    db.session.commit()
