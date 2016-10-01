# -*- coding: utf-8 -*-

"""
byceps.services.orga_team.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...database import db

from .models import Membership


def find_membership_for_party(user_id, party_id):
    """Return the user's membership in an orga team of that party."""
    return Membership.query \
        .filter_by(user_id=user_id) \
        .for_party_id(party_id) \
        .one_or_none()


def get_memberships_for_party(party_id):
    """Return all orga team memberships for that party."""
    return Membership.query \
        .for_party_id(party_id) \
        .options(
            db.joinedload('orga_team'),
            db.joinedload('user').load_only('id', 'screen_name'),
            db.joinedload('user').joinedload('detail').load_only('first_names', 'last_name'),
            db.joinedload('user').joinedload('orga_team_memberships'),
        ) \
        .all()
