# -*- coding: utf-8 -*-

"""
byceps.blueprints.user_badge.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from collections import defaultdict

from ...database import db

from .models import Badge, BadgeAwarding


def create_badge(label, image_filename, *, description=None):
    """Introduce a new badge."""
    badge = Badge(label, image_filename, description=description)

    db.session.add(badge)
    db.session.commit()

    return badge


def find_badge(badge_id):
    """Return the badge with that id, or `None` if not found."""
    return Badge.query.get(badge_id)


def get_awardings_of_badge(badge_id):
    """Return the awardings (user and date) of this badge."""
    return BadgeAwarding.query \
        .filter_by(badge_id=badge_id) \
        .all()


def get_badges_for_user(user_id):
    """Return all badges that have been awarded to the user."""
    return Badge.query \
        .join(BadgeAwarding).filter_by(user_id=user_id) \
        .all()


def get_badges_for_users(user_ids):
    """Return all badges that have been awarded to the users, indexed
    by user ID.
    """
    awardings = BadgeAwarding.query \
        .filter(BadgeAwarding.user_id.in_(user_ids)) \
        .options(
            db.joinedload(BadgeAwarding.badge),
        ) \
        .all()

    badges_by_user_id = defaultdict(set)
    for awarding in awardings:
        badges_by_user_id[awarding.user_id].add(awarding.badge)

    return dict(badges_by_user_id)

def get_all_badges():
    """Return all badges."""
    return Badge.query.all()


def award_badge_to_user(badge, user):
    """Award the badge to the user."""
    badge.recipients.add(user)
    db.session.commit()
