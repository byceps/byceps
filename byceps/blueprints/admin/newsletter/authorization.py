"""
byceps.blueprints.admin.newsletter.authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.util.authorization import create_permission_enum


NewsletterPermission = create_permission_enum('newsletter', [
    'export_subscribers',
    'view_subscriptions',
])
