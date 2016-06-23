# -*- coding: utf-8 -*-

"""
byceps.blueprints.orga.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...database import db

from .models import Membership


def get_team_memberships_for_party(party):
    return Membership.query \
        .for_party(party) \
        .options(
            db.joinedload('orga_team'),
            db.joinedload('user').load_only('id', 'screen_name'),
            db.joinedload('user').joinedload('detail').load_only('first_names', 'last_name'),
            db.joinedload('user').joinedload('orga_team_memberships'),
        ) \
        .all()


def find_orga_team_membership_for_party(user, party):
    """Return the user's membership in an orga team of that party."""
    return Membership.query \
        .filter_by(user=user) \
        .for_party(party) \
        .one_or_none()
