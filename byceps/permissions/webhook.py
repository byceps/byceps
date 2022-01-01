"""
byceps.permissions.webhook
~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext

from ..util.authorization import register_permissions


register_permissions(
    'webhook',
    [
        ('administrate', lazy_gettext('Administrate webhooks')),
        ('view', lazy_gettext('View webhooks')),
    ],
)
