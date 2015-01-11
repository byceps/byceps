# -*- coding: utf-8 -*-

"""
byceps.blueprints.newsletter_admin.authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
"""

from byceps.util.authorization import create_permission_enum


NewsletterPermission = create_permission_enum('newsletter', [
    'export_subscribers',
    'view_subscriptions',
])
