"""
byceps.permissions.party
~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext

from ..util.authorization import register_permissions


register_permissions(
    'party',
    [
        ('create', lazy_gettext('Create parties')),
        ('update', lazy_gettext('Edit parties')),
        ('view', lazy_gettext('View parties')),
    ],
)
