# -*- coding: utf-8 -*-

"""
byceps.util.auth
~~~~~~~~~~~~~~~~

Authorization utilities.

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from enum import Enum


def create_permission_enum(name_prefix, permission_names):
    name = '{}Permission'.format(name_prefix)
    permission_enum = Enum(name, list(permission_names))
    permission_enum.__repr__ = lambda self: '<{}>'.format(self)
    return permission_enum
