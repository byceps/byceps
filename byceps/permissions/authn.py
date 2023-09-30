"""
byceps.permissions.authn
~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2022-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext

from byceps.util.authz import register_permissions


register_permissions(
    'authn_identity_tag',
    [
        ('administrate', lazy_gettext('Administrate user identity tags')),
        ('view', lazy_gettext('View user identity tags')),
    ],
)
