# -*- coding: utf-8 -*-

"""
:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.blueprints.authorization.registry import PermissionRegistry
from byceps.util.authorization import create_permission_enum


ItemPermission = create_permission_enum('item', ['view', 'create', 'update'])


def test_lookup_of_existing_enum_member():
    registry = create_registry_with_registered_enum()

    permission_id = 'item.create'

    assert registry.get_enum_member(permission_id) == ItemPermission.create


def test_lookup_of_nonexistent_member_of_existing_enum():
    registry = create_registry_with_registered_enum()

    permission_id = 'item.delete'

    assert registry.get_enum_member(permission_id) == None


def test_lookup_of_member_of_nonexistent_enum():
    registry = create_registry_with_registered_enum()

    permission_id = 'article.create'

    assert registry.get_enum_member(permission_id) == None


def create_registry_with_registered_enum():
    registry = PermissionRegistry()
    registry.register_enum(ItemPermission)
    return registry
