"""
byceps.blueprints.admin.shop.order.authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.util.authorization import create_permission_enum


ShopOrderPermission = create_permission_enum(
    'shop_order',
    [
        'cancel',
        'mark_as_paid',
        'update',
        'view',
    ],
)
