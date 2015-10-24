# -*- coding: utf-8 -*-

"""
byceps.blueprints.orga.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import g

from ...database import db

from .models import Membership, OrgaTeam


def get_team_memberships_for_current_party():
    return Membership.query \
        .join(OrgaTeam).filter(OrgaTeam.party == g.party) \
        .options(
            db.joinedload('orga_team'),
            db.joinedload('user').load_only('id', 'screen_name', 'avatar_image_created_at', '_avatar_image_type'),
            db.joinedload('user').joinedload('detail').load_only('first_names', 'last_name'),
            db.joinedload('user').joinedload('orga_flags'),
        ) \
        .all()


def find_orga_team_membership_for_current_party(user):
    """Return the user's membership in an orga team of the current party."""
    memberships_for_current_party = list(filter(
        lambda m: m.orga_team.party == g.party,
        user.orga_team_memberships))

    if len(memberships_for_current_party) > 2:
        raise Exception(
            'A user must only be part of one orga team per party.')

    if memberships_for_current_party:
        return memberships_for_current_party[0]
