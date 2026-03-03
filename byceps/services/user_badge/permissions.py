"""
byceps.services.user_badge.permissions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext

from byceps.util.authz import register_permissions


register_permissions(
    'user_badge',
    [
        ('award', lazy_gettext('Award user badges')),
        ('create', lazy_gettext('Create user badges')),
        ('update', lazy_gettext('Edit user badges')),
        ('view', lazy_gettext('View user badges')),
    ],
)
