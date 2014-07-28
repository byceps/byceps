# -*- coding: utf-8 -*-

"""
byceps.blueprints.contentpage.authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from byceps.util.authorization import create_permission_enum


ContentPagePermission = create_permission_enum('ContentPage', [
    'list',
    'create',
    'update',
    'view_history',
])
