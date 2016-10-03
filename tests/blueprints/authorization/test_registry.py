# -*- coding: utf-8 -*-

"""
:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from nose2.tools import params

from byceps.blueprints.authorization.registry import PermissionRegistry
from byceps.util.authorization import create_permission_enum


ItemPermission = create_permission_enum('item', ['view', 'create', 'update'])


@params(
    ('item.create'   , ItemPermission.create),  # enum member exists
    ('item.delete'   , None                 ),  # enum exists, but member does not
    ('article.create', None                 ),  # enum does not exist
)
def test_lookup(permission_id, expected):
    registry = create_registry_with_registered_enum()

    assert registry.get_enum_member(permission_id) == expected


def create_registry_with_registered_enum():
    registry = PermissionRegistry()
    registry.register_enum(ItemPermission)
    return registry
