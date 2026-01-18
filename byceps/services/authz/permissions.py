"""
byceps.services.authz.permissions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext

from byceps.util.authz import register_permissions


register_permissions(
    'role',
    [
        ('assign', lazy_gettext('Assign roles')),
        ('view', lazy_gettext('View roles')),
    ],
)
