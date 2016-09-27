# -*- coding: utf-8 -*-

"""
:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from nose2.tools import params

from byceps.services.authorization.models import Permission
from byceps.util.authorization import create_permission_enum


ExamplePermission = create_permission_enum('example', ['one', 'two', 'three'])

MultiWordPermission = create_permission_enum('multi_word', ['foo', 'bar'])


@params(
    (ExamplePermission.one,   'example.one'   ),
    (ExamplePermission.three, 'example.three' ),
    (MultiWordPermission.foo, 'multi_word.foo'),
)
def test_creation_from_enum_member(enum_member, expected):
    actual = Permission.from_enum_member(enum_member)

    assert actual.id == expected
