# -*- coding: utf-8 -*-

"""
bootstrap.helpers
~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.blueprints.brand.models import Brand
from byceps.blueprints.party.models import Party
from byceps.blueprints.user.models.user import User
from byceps.blueprints.user import service as user_service
from byceps.blueprints.user_group.models import UserGroup
from byceps.services.orga.models import OrgaFlag
from byceps.services.orga_team.models import OrgaTeam, \
    Membership as OrgaTeamMembership
from byceps.services.seating.models.area import Area as SeatingArea
from byceps.services.seating.models.category import Category as SeatingCategory
from byceps.services.seating.models.seat import Seat
from byceps.services.snippet.models.mountpoint import \
    Mountpoint as SnippetMountpoint
from byceps.services.snippet.models.snippet import Snippet, SnippetVersion
from byceps.services.terms.models import Version as TermsVersion

from .util import add_to_database


# -------------------------------------------------------------------- #
# brands


@add_to_database
def create_brand(brand_id, title):
    return Brand(brand_id, title)


def get_brand(brand_id):
    return Brand.query.get(brand_id)


# -------------------------------------------------------------------- #
# parties


@add_to_database
def create_party(**kwargs):
    return Party(**kwargs)


def get_party(party_id):
    return Party.query.get(party_id)


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


# -------------------------------------------------------------------- #
# snippets


@add_to_database
def create_snippet(party, name, type_):
    return Snippet(party, name, type_)


@add_to_database
def create_snippet_version(snippet, creator, title, body):
    return SnippetVersion(snippet=snippet, creator=creator, title=title, body=body)


@add_to_database
def mount_snippet(snippet, endpoint_suffix, url_path):
    return SnippetMountpoint(snippet=snippet, endpoint_suffix=endpoint_suffix, url_path=url_path)


# -------------------------------------------------------------------- #
# terms


@add_to_database
def create_terms_version(brand, creator, title, body):
    return TermsVersion(brand.id, creator.id, title, body)


# -------------------------------------------------------------------- #
# seating


@add_to_database
def create_seating_area(party, slug, title):
    return SeatingArea(party.id, slug, title)


@add_to_database
def create_seat_category(party, title):
    return SeatingCategory(party.id, title)


@add_to_database
def create_seat(area, coord_x, coord_y, category):
    return Seat(area, category, coord_x=coord_x, coord_y=coord_y)
