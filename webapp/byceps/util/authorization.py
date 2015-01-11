# -*- coding: utf-8 -*-

"""
byceps.util.authorization
~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
"""

from enum import Enum


def create_permission_enum(key, member_names):
    """Create a permission enum."""
    name = derive_name(key)
    permission_enum = Enum(name, list(member_names))
    permission_enum.__key__ = key
    permission_enum.__repr__ = lambda self: '<{}>'.format(self)
    return permission_enum


def derive_name(key):
    """Derive a CameCase name from the underscore_separated_key."""
    words = key.split('_')
    words.append('permission')
    words = (word.title() for word in words)
    return ''.join(words)
