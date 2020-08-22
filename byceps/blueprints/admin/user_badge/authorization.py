"""
byceps.blueprints.admin.user_badge.authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.util.authorization import create_permission_enum


UserBadgePermission = create_permission_enum('user_badge', [
    'award',
    'create',
    'update',
])
