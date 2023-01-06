"""
byceps.permissions.authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext

from ..util.authorization import register_permissions


register_permissions(
    'role',
    [
        ('assign', lazy_gettext('Assign roles')),
        ('view', lazy_gettext('View roles')),
    ],
)
