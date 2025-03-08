"""
byceps.services.orga.permissions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext

from byceps.util.authz import register_permissions


register_permissions(
    'orga_birthday',
    [
        ('view', lazy_gettext("View orgas' birthdays")),
    ],
)


register_permissions(
    'orga_detail',
    [
        ('view', lazy_gettext("View orgas' details")),
    ],
)
