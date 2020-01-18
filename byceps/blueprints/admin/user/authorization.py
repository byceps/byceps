"""
byceps.blueprints.admin.user.authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.util.authorization import create_permission_enum


UserPermission = create_permission_enum('user', [
    'administrate',
    'create',
    'set_password',
    'view',
])
