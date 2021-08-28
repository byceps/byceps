"""
byceps.permissions.admin
~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ..util.authorization import create_permission_enum


AdminPermission = create_permission_enum(
    'admin',
    [
        'access',
        'maintain',
    ],
)
