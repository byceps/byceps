"""
byceps.services.whereabouts.permissions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2022-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext

from byceps.util.authz import register_permissions


register_permissions(
    'whereabouts',
    [
        ('administrate', lazy_gettext('Administrate whereabouts')),
        ('update', lazy_gettext('Update whereabouts')),
        ('view', lazy_gettext('View whereabouts')),
    ],
)
