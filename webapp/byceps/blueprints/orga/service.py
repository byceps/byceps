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
