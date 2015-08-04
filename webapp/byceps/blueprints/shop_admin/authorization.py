# -*- coding: utf-8 -*-

"""
byceps.blueprints.shop_admin.authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.util.authorization import create_permission_enum


ShopArticlePermission = create_permission_enum('shop_article', [
    'create',
    'update',
    'list',
    'view',
])


ShopOrderPermission = create_permission_enum('shop_order', [
    'update',
    'list',
    'view',
])
