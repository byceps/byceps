"""
byceps.blueprints.admin.shop.shop.authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.util.authorization import create_permission_enum


ShopPermission = create_permission_enum(
    'shop',
    [
        'create',
        'update',
        'view',
    ],
)
