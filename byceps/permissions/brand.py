"""
byceps.permissions.brand
~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext

from byceps.util.authorization import register_permissions


register_permissions(
    'brand',
    [
        ('create', lazy_gettext('Create brands')),
        ('update', lazy_gettext('Edit brands')),
        ('view', lazy_gettext('View brands')),
    ],
)
