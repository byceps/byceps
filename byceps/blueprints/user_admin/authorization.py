"""
byceps.blueprints.user_admin.authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.util.authorization import create_permission_enum


UserPermission = create_permission_enum('user', [
    'administrate',
    'list',
    'set_password',
    'view',
])
