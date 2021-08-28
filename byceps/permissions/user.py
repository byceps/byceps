"""
byceps.permissions.user
~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ..util.authorization import create_permission_enum


UserPermission = create_permission_enum(
    'user',
    [
        'administrate',
        'create',
        'set_password',
        'view',
    ],
)
