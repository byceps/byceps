# -*- coding: utf-8 -*-

from unittest import TestCase

from nose2.tools import params

from byceps.blueprints.authorization.models import Permission
from byceps.util.authorization import create_permission_enum


ExamplePermission = create_permission_enum('example', ['one', 'two', 'three'])

MultiWordPermission = create_permission_enum('multi_word', ['foo', 'bar'])


class PermissionTestCase(TestCase):

    @params(
        (ExamplePermission.one,   'example.one'   ),
        (ExamplePermission.three, 'example.three' ),
        (MultiWordPermission.foo, 'multi_word.foo'),
    )
    def test_creation_from_enum_member(self, enum_member, expected):
        actual = Permission.from_enum_member(enum_member)

        self.assertEquals(actual.id, expected)
