"""
byceps.blueprints.newsletter_admin.authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.util.authorization import create_permission_enum


NewsletterPermission = create_permission_enum('newsletter', [
    'export_subscribers',
    'view_subscriptions',
])
