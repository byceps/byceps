# -*- coding: utf-8 -*-

"""
byceps.blueprints.user_admin.authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from byceps.util.authorization import create_permission_enum


UserPermission = create_permission_enum('user', [
    'list',
])
