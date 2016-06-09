# -*- coding: utf-8 -*-

"""
:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from unittest import TestCase

from nose2.tools import params

from byceps.util.authorization import create_permission_enum


class PermissionEnumTestCase(TestCase):

    @params(
        ('user',      ),
        ('board_topic'),
    )
    def test_key(self, key):
        enum = create_permission_enum(key, ['some_member'])

        assert enum.__key__ == key

    @params(
        ('user',        'UserPermission'      ),
        ('board_topic', 'BoardTopicPermission'),
        ('foo_bar_baz', 'FooBarBazPermission' ),
        ('CASe_FReNzY', 'CaseFrenzyPermission'),
    )
    def test_name_derivation(self, key, expected):
        enum = create_permission_enum(key, ['some_member'])

        actual = enum.some_member.__class__.__name__

        assert actual == expected

    def test_member_names(self):
        member_names = ['one', 'two', 'three']

        enum = create_permission_enum('example', member_names)

        actual = list(enum.__members__)

        assert actual == member_names
