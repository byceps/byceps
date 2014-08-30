# -*- coding: utf-8 -*-

"""
byceps.blueprints.authorization_admin.authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from byceps.util.authorization import create_permission_enum


RolePermission = create_permission_enum('role', [
    'list',
])
