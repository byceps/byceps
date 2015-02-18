# -*- coding: utf-8 -*-

"""
byceps.blueprints.news_admin.authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
"""

from byceps.util.authorization import create_permission_enum


NewsItemPermission = create_permission_enum('news_item', [
    'create',
    'list',
])
