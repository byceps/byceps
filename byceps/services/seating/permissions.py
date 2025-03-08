"""
byceps.services.seating.permissions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext

from byceps.util.authz import register_permissions


register_permissions(
    'seating',
    [
        ('administrate', lazy_gettext('Administrate seating')),
        ('view', lazy_gettext('View seating administration')),
    ],
)
