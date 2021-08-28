"""
byceps.permissions.shop_shop
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ..util.authorization import create_permission_enum


ShopPermission = create_permission_enum(
    'shop',
    [
        'create',
        'update',
        'view',
    ],
)


ShopArticlePermission = create_permission_enum(
    'shop_article',
    [
        'create',
        'update',
        'view',
    ],
)


ShopOrderPermission = create_permission_enum(
    'shop_order',
    [
        'cancel',
        'mark_as_paid',
        'update',
        'view',
    ],
)
