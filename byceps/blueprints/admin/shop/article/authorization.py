"""
byceps.blueprints.admin.shop.article.authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.util.authorization import create_permission_enum


ShopArticlePermission = create_permission_enum('shop_article', [
    'create',
    'update',
    'view',
])
