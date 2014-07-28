# -*- coding: utf-8 -*-

from enum import Enum
from unittest import TestCase

from byceps.blueprints.authorization.models import Permission
from byceps.blueprints.authorization.registry import PermissionRegistry


class PermissionRegistryTestCase(TestCase):

    def setUp(self):
        self.registry = PermissionRegistry()
        self.registry.register_enum('item', ItemPermission)

    def test_lookup_of_existing_enum_member(self):
        permission = Permission(id='item.create')
        self.assert_get_enum_member_equals(permission, ItemPermission.create)

    def test_lookup_of_nonexistent_member_of_existing_enum(self):
        permission = Permission(id='item.delete')
        self.assert_get_enum_member_equals(permission, None)

    def test_lookup_of_member_of_nonexistent_enum(self):
        permission = Permission(id='article.create')
        self.assert_get_enum_member_equals(permission, None)

    def assert_get_enum_member_equals(self, permission, expected):
        actual = self.registry.get_enum_member(permission)
        self.assertEqual(actual, expected)


ItemPermission = Enum('ItemPermission', 'view create update')
