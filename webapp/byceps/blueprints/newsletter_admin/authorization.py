# -*- coding: utf-8 -*-

"""
byceps.blueprints.newsletter_admin.authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from byceps.util.authorization import create_permission_enum


NewsletterPermission = create_permission_enum('newsletter', [
    'view_subscriptions',
])
