"""
byceps.permissions.gallery
~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext

from byceps.util.authz import register_permissions


register_permissions(
    'gallery',
    [
        ('administrate', lazy_gettext('Administrate galleries')),
        ('view_hidden', lazy_gettext('View hidden galleries and images')),
    ],
)
