"""
byceps.permissions.webhook
~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext

from byceps.util.authorization import register_permissions


register_permissions(
    'webhook',
    [
        ('administrate', lazy_gettext('Administrate webhooks')),
        ('view', lazy_gettext('View webhooks')),
    ],
)
