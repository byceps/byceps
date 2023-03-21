"""
byceps.permissions.newsletter
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import lazy_gettext

from ..util.authorization import register_permissions


register_permissions(
    'newsletter',
    [
        ('administrate', lazy_gettext('Administrate newsletter subscription lists')),
        ('export_subscribers', lazy_gettext('Export newsletter subscribers')),
        ('view_subscriptions', lazy_gettext('View newsletter subscriptions')),
    ],
)
