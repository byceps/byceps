# -*- coding: utf-8 -*-

"""
bootstrap.helpers
~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.blueprints.user_group.models import UserGroup
from byceps.services.orga.models import OrgaFlag
from byceps.services.orga_team.models import OrgaTeam, \
    Membership as OrgaTeamMembership
from byceps.services.user.models.user import User
from byceps.services.user import service as user_service

from .util import add_to_database


# -------------------------------------------------------------------- #
# users


@add_to_database
def create_user(screen_name, email_address, *, enabled=False):
    user = user_service.build_user(screen_name, email_address)
    user.enabled = enabled
    return user


def find_user(screen_name):
    return User.query.filter_by(screen_name=screen_name).one_or_none()


def get_user(screen_name):
    return User.query.filter_by(screen_name=screen_name).one()


# -------------------------------------------------------------------- #
# orga teams


@add_to_database
def promote_orga(brand, user):
    return OrgaFlag(brand.id, user.id)


@add_to_database
def create_orga_team(party, title):
    return OrgaTeam(party.id, title.id)


@add_to_database
def assign_user_to_orga_team(user, orga_team, *, duties=None):
    membership = OrgaTeamMembership(orga_team.id, user.id)
    if duties:
        membership.duties = duties
    return membership


def get_orga_team(team_id):
    return OrgaTeam.query.get(team_id)


# -------------------------------------------------------------------- #
# user groups


@add_to_database
def create_user_group(creator, title, description=None):
    return UserGroup(creator, title, description)
