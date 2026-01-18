"""
byceps.services.brand.permissions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext

from byceps.util.authz import register_permissions


register_permissions(
    'brand',
    [
        ('create', lazy_gettext('Create brands')),
        ('update', lazy_gettext('Edit brands')),
        ('view', lazy_gettext('View brands')),
    ],
)
