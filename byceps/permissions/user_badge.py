"""
byceps.permissions.user_badge
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ..util.authorization import create_permission_enum


UserBadgePermission = create_permission_enum(
    'user_badge',
    [
        'award',
        'create',
        'update',
        'view',
    ],
)
