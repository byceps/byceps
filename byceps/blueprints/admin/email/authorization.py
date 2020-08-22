"""
byceps.blueprints.admin.email.authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.util.authorization import create_permission_enum


EmailConfigPermission = create_permission_enum('email_config', [
    'create',
    'update',
    'view',
])
