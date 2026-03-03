"""
byceps.services.guest_server.permissions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext

from byceps.util.authz import register_permissions


register_permissions(
    'guest_server',
    [
        ('administrate', lazy_gettext('Administrate guest servers')),
        ('view', lazy_gettext('View guest servers')),
    ],
)
