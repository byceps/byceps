"""
byceps.services.user.permissions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext

from byceps.util.authz import register_permissions


register_permissions(
    'user',
    [
        ('administrate', lazy_gettext('Administrate users')),
        ('create', lazy_gettext('Create users')),
        ('set_password', lazy_gettext('Set user passwords')),
        ('view', lazy_gettext('View users')),
    ],
)
