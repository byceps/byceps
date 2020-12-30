"""
byceps.blueprints.admin.webhook.authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.util.authorization import create_permission_enum


WebhookPermission = create_permission_enum('webhook', [
    'administrate',
    'view',
])
