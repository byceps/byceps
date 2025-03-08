"""
byceps.services.party.permissions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext

from byceps.util.authz import register_permissions


register_permissions(
    'party',
    [
        ('create', lazy_gettext('Create parties')),
        ('update', lazy_gettext('Edit parties')),
        ('view', lazy_gettext('View parties')),
    ],
)
