"""
byceps.blueprints.admin.shop.article.authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.util.authorization import create_permission_enum


ShopArticlePermission = create_permission_enum('shop_article', [
    'create',
    'update',
    'view',
])
