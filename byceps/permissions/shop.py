"""
byceps.permissions.shop_shop
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ..util.authorization import register_permissions


register_permissions(
    'shop',
    [
        'create',
        'update',
        'view',
    ],
)


register_permissions(
    'shop_article',
    [
        'create',
        'update',
        'view',
    ],
)


register_permissions(
    'shop_order',
    [
        'cancel',
        'mark_as_paid',
        'update',
        'view',
    ],
)
