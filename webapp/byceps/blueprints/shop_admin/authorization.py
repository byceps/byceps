# -*- coding: utf-8 -*-

"""
byceps.blueprints.shop_admin.authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
"""

from byceps.util.authorization import create_permission_enum


ShopPermission = create_permission_enum('shop', [
    'list_articles',
    'list_orders',
    'update_orders',
])
