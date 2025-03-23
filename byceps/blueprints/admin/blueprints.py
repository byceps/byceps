"""
byceps.application.blueprints.admin.blueprints
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import Flask

from byceps.blueprints.common.blueprints import get_common_blueprints
from byceps.util.framework.blueprint import register_blueprints


def register_admin_blueprints(
    app: Flask, *, style_guide_enabled: bool = False
) -> None:
    common_blueprints = get_common_blueprints(
        style_guide_enabled=style_guide_enabled
    )

    blueprints = common_blueprints + [
        ('blueprints.admin.api', '/api'),
        ('services.attendance.blueprints.admin', '/attendance'),
        (
            'blueprints.admin.authn.identity_tag',
            '/authentication/identity_tags',
        ),
        ('blueprints.admin.authn.login', '/authentication'),
        ('blueprints.admin.authz', '/authorization'),
        ('blueprints.admin.board', '/boards'),
        ('blueprints.admin.brand', '/brands'),
        ('blueprints.admin.consent', '/consent'),
        ('blueprints.admin.core', '/'),
        ('blueprints.admin.dashboard', '/dashboard'),
        ('blueprints.admin.demo_data', '/demo_data'),
        ('blueprints.admin.gallery', '/galleries'),
        ('blueprints.admin.guest_server', '/guest_servers'),
        ('blueprints.admin.jobs', '/jobs'),
        ('blueprints.admin.language', '/languages'),
        ('blueprints.admin.maintenance', '/maintenance'),
        ('blueprints.admin.more', '/more'),
        ('blueprints.admin.news', '/news'),
        ('blueprints.admin.newsletter', '/newsletter'),
        ('blueprints.admin.orga', '/orgas'),
        ('blueprints.admin.orga_presence', '/presence'),
        ('blueprints.admin.orga_team', '/orga_teams'),
        ('blueprints.admin.page', '/pages'),
        ('blueprints.admin.party', '/parties'),
        ('blueprints.admin.seating', '/seating'),
        ('blueprints.admin.shop', None),
        (
            'blueprints.admin.shop.cancellation_request',
            '/shop/cancellation_requests',
        ),
        ('blueprints.admin.shop.catalog', '/shop/catalogs'),
        ('blueprints.admin.shop.email', '/shop/email'),
        ('blueprints.admin.shop.order', '/shop/orders'),
        ('blueprints.admin.shop.payment', '/shop/payment'),
        ('blueprints.admin.shop.product', '/shop/products'),
        ('blueprints.admin.shop.shipping', '/shop/shipping'),
        ('blueprints.admin.shop.shop', '/shop/shop'),
        ('blueprints.admin.shop.sold_products', '/shop/sold_products'),
        ('blueprints.admin.shop.storefront', '/shop/storefronts'),
        ('blueprints.admin.site', '/sites'),
        ('blueprints.admin.site.navigation', '/sites/navigation'),
        ('blueprints.admin.snippet', '/snippets'),
        ('blueprints.admin.ticketing', '/ticketing'),
        ('blueprints.admin.ticketing.category', '/ticketing/categories'),
        ('blueprints.admin.ticketing.checkin', '/ticketing/checkin'),
        ('blueprints.admin.timetable', '/timetables'),
        ('blueprints.admin.tourney', None),
        ('blueprints.admin.tourney.category', '/tourney/categories'),
        ('blueprints.admin.tourney.tourney', '/tourney/tourneys'),
        ('blueprints.admin.user', '/users'),
        ('blueprints.admin.user_badge', '/user_badges'),
        ('blueprints.admin.webhook', '/webhooks'),
    ]

    register_blueprints(app, blueprints)
