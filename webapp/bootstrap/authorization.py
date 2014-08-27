# -*- coding: utf-8 -*-

from byceps.blueprints.authorization.models import Permission, Role, \
    RolePermission, UserRole
from byceps.blueprints.board.authorization import BoardPostingPermission, \
    BoardTopicPermission
from byceps.blueprints.orga_admin.authorization import OrgaTeamPermission
from byceps.blueprints.party_admin.authorization import PartyPermission
from byceps.blueprints.snippet_admin.authorization import SnippetPermission
from byceps.blueprints.user_admin.authorization import UserPermission
from byceps.database import db

from .util import add_all_to_database, add_to_database


def create_roles_and_permissions():
    create_role_with_permissions_from_enum_members('board_user', [
        BoardPostingPermission.create,
        BoardPostingPermission.update,
        BoardTopicPermission.create,
    ])
    create_role_with_permissions_from_enum_members('board_moderator', [
        BoardPostingPermission.hide,
        BoardTopicPermission.hide,
        BoardTopicPermission.lock,
        BoardTopicPermission.pin,
    ])
    create_role_with_permissions_from_enum('orga_team_admin', OrgaTeamPermission)
    create_role_with_permissions_from_enum('party_admin', PartyPermission)
    create_role_with_permissions_from_enum('snippet_editor', SnippetPermission)
    create_role_with_permissions_from_enum('user_admin', UserPermission)

    db.session.commit()


# -------------------------------------------------------------------- #
# helpers


def create_role_with_permissions_from_enum(role_name, permission_enum):
    return create_role_with_permissions_from_enum_members(role_name, iter(permission_enum))


def create_role_with_permissions_from_enum_members(role_name, permission_enum_members):
    role = create_role(role_name)
    permissions = create_permissions_from_enum_members(permission_enum_members)
    add_permissions_to_role(permissions, role)


@add_to_database
def create_role(id):
    return Role(id=id)


def get_role(id):
    return Role.query.get(id)


@add_all_to_database
def create_permissions_from_enum_members(enum_members):
    return list(map(Permission.from_enum_member, enum_members))


def add_permissions_to_role(permissions, role):
    for permission in permissions:
        add_permission_to_role(permission, role)


def add_permission_to_role(permission, role):
    # FIXME
    #role.permissions.append(permission)
    role_permission = RolePermission(role=role, permission=permission)
    role.role_permissions.append(role_permission)


def add_roles_to_user(roles, user):
    for role in roles:
        add_role_to_user(role, user)


def add_role_to_user(role, user):
    # FIXME
    #user.roles.append(role)
    user.user_roles.append(UserRole(user=user, role=role))
