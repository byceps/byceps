# -*- coding: utf-8 -*-

from unittest import TestCase

from byceps.blueprints.authorization.models import Permission
from byceps.blueprints.authorization.registry import PermissionRegistry
from byceps.util.authorization import create_permission_enum


class PermissionRegistryTestCase(TestCase):

    def setUp(self):
        self.registry = PermissionRegistry()
        self.registry.register_enum(ItemPermission)

    def test_lookup_of_existing_enum_member(self):
        permission = create_permission('item.create')
        self.assert_get_enum_member_equals(permission, ItemPermission.create)

    def test_lookup_of_nonexistent_member_of_existing_enum(self):
        permission = create_permission('item.delete')
        self.assert_get_enum_member_equals(permission, None)

    def test_lookup_of_member_of_nonexistent_enum(self):
        permission = create_permission('article.create')
        self.assert_get_enum_member_equals(permission, None)

    def assert_get_enum_member_equals(self, permission, expected):
        actual = self.registry.get_enum_member(permission)
        self.assertEqual(actual, expected)


ItemPermission = create_permission_enum('item', ['view', 'create', 'update'])


def create_permission(id):
    return Permission(id=id)
