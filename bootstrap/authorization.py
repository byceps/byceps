# -*- coding: utf-8 -*-

"""
bootstrap.authorization
~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.blueprints.authorization.models import Permission as DbPermission, \
    Role
from byceps.blueprints.authorization_admin.authorization import RolePermission
from byceps.blueprints.board.authorization import BoardPostingPermission, \
    BoardTopicPermission
from byceps.blueprints.orga_admin.authorization import OrgaTeamPermission
from byceps.blueprints.party_admin.authorization import PartyPermission
from byceps.blueprints.snippet_admin.authorization import \
    MountpointPermission, SnippetPermission
from byceps.blueprints.terms_admin.authorization import TermsPermission
from byceps.blueprints.user_admin.authorization import UserPermission
from byceps.database import db

from .util import add_all_to_database, add_to_database


def create_roles_and_permissions():
    create_role_with_permissions_from_enum(
        'authorization_admin',
        'Rechte und Rollen verwalten',
        RolePermission)

    create_role_with_permissions_from_enum_members(
        'board_user',
        'im Forum schreiben',
        [
            BoardPostingPermission.create,
            BoardPostingPermission.update,
            BoardTopicPermission.create,
            BoardTopicPermission.update,
        ])

    create_role_with_permissions_from_enum_members(
        'board_orga',
        'versteckte Themen und Beiträge im Forum lesen',
        [
            BoardPostingPermission.view_hidden,
            BoardTopicPermission.view_hidden
        ])

    create_role_with_permissions_from_enum_members(
        'board_moderator',
        'Forum moderieren',
        [
            BoardPostingPermission.hide,
            BoardTopicPermission.hide,
            BoardTopicPermission.lock,
            BoardTopicPermission.pin,
        ])

    create_role_with_permissions_from_enum(
        'orga_team_admin',
        'Orgateams verwalten',
        OrgaTeamPermission)

    create_role_with_permissions_from_enum(
        'party_admin',
        'Partys verwalten',
        PartyPermission)

    create_role_with_permissions_from_enum(
        'snippet_admin',
        'Snippets verwalten',
        MountpointPermission)

    create_role_with_permissions_from_enum(
        'snippet_editor',
        'Snippets bearbeiten',
        SnippetPermission)

    create_role_with_permissions_from_enum(
        'terms_editor',
        'AGB verwalten',
        TermsPermission)

    create_role_with_permissions_from_enum(
        'user_admin',
        'Benutzer verwalten',
        UserPermission)

    db.session.commit()


# -------------------------------------------------------------------- #
# helpers


def create_role_with_permissions_from_enum(role_id, role_title, permission_enum):
    return create_role_with_permissions_from_enum_members(role_id, role_title, iter(permission_enum))


def create_role_with_permissions_from_enum_members(role_id, role_title, permission_enum_members):
    role = create_role(role_id, role_title)
    permissions = create_permissions_from_enum_members(permission_enum_members)
    add_permissions_to_role(permissions, role)


@add_to_database
def create_role(id, title):
    return Role(id, title)


def get_role(id):
    return Role.query.get(id)


@add_all_to_database
def create_permissions_from_enum_members(enum_members):
    return list(map(DbPermission.from_enum_member, enum_members))


def add_permissions_to_role(permissions, role):
    for permission in permissions:
        role.permissions.add(permission)


def add_roles_to_user(roles, user):
    for role in roles:
        user.roles.add(role)
