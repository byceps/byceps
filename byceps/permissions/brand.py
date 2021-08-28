"""
byceps.permissions.brand
~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ..util.authorization import create_permission_enum


BrandPermission = create_permission_enum(
    'brand',
    [
        'create',
        'update',
        'view',
    ],
)
