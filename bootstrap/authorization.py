# -*- coding: utf-8 -*-

"""
bootstrap.authorization
~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

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
from byceps.services.authorization.models import Permission as DbPermission, \
    Role
from byceps.services.authorization import service as authorization_service

from .util import add_all_to_database, add_to_database


def create_roles_and_permissions():
    create_role_with_permissions_from_enum_members(
        'authorization_admin',
        'Rechte und Rollen verwalten',
        [
            RolePermission.list,
        ])

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

    create_role_with_permissions_from_enum_members(
        'orga_team_admin',
        'Orgateams verwalten',
        [
            OrgaTeamPermission.list,
            OrgaTeamPermission.create,
            OrgaTeamPermission.delete,
            OrgaTeamPermission.administrate_memberships,
        ])

    create_role_with_permissions_from_enum_members(
        'party_admin',
        'Partys verwalten',
        [
            PartyPermission.list,
            PartyPermission.create,
        ])

    create_role_with_permissions_from_enum_members(
        'snippet_admin',
        'Snippets verwalten',
        [
            MountpointPermission.create,
            MountpointPermission.delete,
        ])

    create_role_with_permissions_from_enum_members(
        'snippet_editor',
        'Snippets bearbeiten',
        [
            SnippetPermission.list,
            SnippetPermission.create,
            SnippetPermission.update,
            SnippetPermission.view_history,
        ])

    create_role_with_permissions_from_enum_members(
        'terms_editor',
        'AGB verwalten',
        [
            TermsPermission.list,
            TermsPermission.create,
        ])

    create_role_with_permissions_from_enum_members(
        'user_admin',
        'Benutzer verwalten',
        [
            UserPermission.list,
            UserPermission.view,
        ])

    db.session.commit()


# -------------------------------------------------------------------- #
# helpers


def create_role_with_permissions_from_enum_members(role_id, role_title, permission_enum_members):
    role = create_role(role_id, role_title)
    permissions = create_permissions_from_enum_members(permission_enum_members)
    add_permissions_to_role(permissions, role)


@add_to_database
def create_role(role_id, title):
    return Role(role_id, title)


def get_role(role_id):
    return Role.query.get(role_id)


@add_all_to_database
def create_permissions_from_enum_members(enum_members):
    return list(map(DbPermission.from_enum_member, enum_members))


def add_permissions_to_role(permissions, role):
    for permission in permissions:
        authorization_service.assign_permission_to_role(permission, role)


def add_roles_to_user(roles, user):
    for role in roles:
        authorization_service.assign_role_to_user(role, user)
