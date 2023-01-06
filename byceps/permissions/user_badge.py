"""
byceps.permissions.user_badge
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext

from ..util.authorization import register_permissions


register_permissions(
    'user_badge',
    [
        ('award', lazy_gettext('Award user badges')),
        ('create', lazy_gettext('Create user badges')),
        ('update', lazy_gettext('Edit user badges')),
        ('view', lazy_gettext('View user badges')),
    ],
)
