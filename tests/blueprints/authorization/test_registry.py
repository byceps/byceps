# -*- coding: utf-8 -*-

"""
:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.blueprints.authorization.models import Permission
from byceps.blueprints.authorization.registry import PermissionRegistry
from byceps.util.authorization import create_permission_enum


ItemPermission = create_permission_enum('item', ['view', 'create', 'update'])


def test_lookup_of_existing_enum_member():
    registry = create_registry_with_registered_enum()

    permission = create_permission('item.create')

    assert registry.get_enum_member(permission) == ItemPermission.create


def test_lookup_of_nonexistent_member_of_existing_enum():
    registry = create_registry_with_registered_enum()

    permission = create_permission('item.delete')

    assert registry.get_enum_member(permission) == None


def test_lookup_of_member_of_nonexistent_enum():
    registry = create_registry_with_registered_enum()

    permission = create_permission('article.create')

    assert registry.get_enum_member(permission) == None


def create_registry_with_registered_enum():
    registry = PermissionRegistry()
    registry.register_enum(ItemPermission)
    return registry


def create_permission(id):
    return Permission(id=id)
