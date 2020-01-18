"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.util.authorization import create_permission_enum


@pytest.mark.parametrize('key', [
    ('user'       ),
    ('board_topic'),
])
def test_key(key):
    enum = create_permission_enum(key, ['some_member'])

    assert enum.__key__ == key


@pytest.mark.parametrize('key, expected', [
    ('user',        'UserPermission'      ),
    ('board_topic', 'BoardTopicPermission'),
    ('foo_bar_baz', 'FooBarBazPermission' ),
    ('CASe_FReNzY', 'CaseFrenzyPermission'),
])
def test_name_derivation(key, expected):
    enum = create_permission_enum(key, ['some_member'])

    actual = enum.some_member.__class__.__name__

    assert actual == expected


def test_member_names():
    member_names = ['one', 'two', 'three']

    enum = create_permission_enum('example', member_names)

    actual = list(enum.__members__)

    assert actual == member_names
