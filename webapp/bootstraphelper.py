#!/usr/bin/env python
# -*- coding: utf-8 -*-

from byceps.blueprints.authorization.models import Permission, Role, \
    RolePermission, UserRole
from byceps.blueprints.brand.models import Brand
from byceps.blueprints.orga.models import OrgaTeam, \
    Membership as OrgaTeamMembership
from byceps.blueprints.party.models import Party
from byceps.blueprints.user.models import User
from byceps.database import db


# -------------------------------------------------------------------- #
# decorators


def add_to_database(f):
    def decorated(*args, **kwargs):
        entity = f(*args, **kwargs)
        db.session.add(entity)
        return entity
    return decorated


def add_all_to_database(f):
    def decorated(*args, **kwargs):
        entities = f(*args, **kwargs)
        for entity in entities:
            db.session.add(entity)
        return entities
    return decorated


# -------------------------------------------------------------------- #
# helpers


@add_to_database
def create_brand(id, title):
    return Brand(id=id, title=title)


@add_to_database
def create_party(**kwargs):
    return Party(**kwargs)


def get_party(id):
    return Party.query.get(id)


@add_to_database
def create_role(id):
    return Role(id=id)


def get_role(id):
    return Role.query.get(id)


@add_all_to_database
def create_permissions(key, enum):
    return list(get_permission_entities_for_enum(key, enum))


def get_permission_entities_for_enum(key, enum):
    for member_name in enum.__members__:
        id = '{}.{}'.format(key, member_name)
        yield Permission(id=id)


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


@add_to_database
def create_orga_team(id, title):
    return OrgaTeam(id=id, title=title)


@add_to_database
def assign_user_to_orga_team(user, orga_team):
    return OrgaTeamMembership(orga_team=orga_team, user=user)


@add_to_database
def create_user(screen_name, email_address, password, *, enabled=False):
    user = User.create(screen_name, email_address, password)
    user.is_enabled = enabled
    return user


def get_user(screen_name):
    return User.query.filter_by(screen_name=screen_name).one()
