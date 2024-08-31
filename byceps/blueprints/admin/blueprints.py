"""
byceps.application.blueprints.admin.blueprints
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2024 Jochen Kupperschmidt
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
        ('admin.api', '/api'),
        ('admin.attendance', '/attendance'),
        ('admin.authn.identity_tag', '/authentication/identity_tags'),
        ('admin.authn.login', '/authentication'),
        ('admin.authz', '/authorization'),
        ('admin.board', '/boards'),
        ('admin.brand', '/brands'),
        ('admin.consent', '/consent'),
        ('admin.core', '/'),
        ('admin.dashboard', '/dashboard'),
        ('admin.demo_data', '/demo_data'),
        ('admin.gallery', '/galleries'),
        ('admin.guest_server', '/guest_servers'),
        ('admin.jobs', '/jobs'),
        ('admin.language', '/languages'),
        ('admin.maintenance', '/maintenance'),
        ('admin.more', '/more'),
        ('admin.news', '/news'),
        ('admin.newsletter', '/newsletter'),
        ('admin.orga', '/orgas'),
        ('admin.orga_presence', '/presence'),
        ('admin.orga_team', '/orga_teams'),
        ('admin.page', '/pages'),
        ('admin.party', '/parties'),
        ('admin.seating', '/seating'),
        ('admin.shop', None),
        ('admin.shop.cancellation_request', '/shop/cancellation_requests'),
        ('admin.shop.catalog', '/shop/catalogs'),
        ('admin.shop.email', '/shop/email'),
        ('admin.shop.order', '/shop/orders'),
        ('admin.shop.paid_products_report', '/shop/paid_products_reports'),
        ('admin.shop.payment', '/shop/payment'),
        ('admin.shop.product', '/shop/products'),
        ('admin.shop.shipping', '/shop/shipping'),
        ('admin.shop.shop', '/shop/shop'),
        ('admin.shop.storefront', '/shop/storefronts'),
        ('admin.site', '/sites'),
        ('admin.site.navigation', '/sites/navigation'),
        ('admin.snippet', '/snippets'),
        ('admin.ticketing', '/ticketing'),
        ('admin.ticketing.category', '/ticketing/categories'),
        ('admin.ticketing.checkin', '/ticketing/checkin'),
        ('admin.timetable', '/timetables'),
        ('admin.tourney', None),
        ('admin.tourney.category', '/tourney/categories'),
        ('admin.tourney.tourney', '/tourney/tourneys'),
        ('admin.user', '/users'),
        ('admin.user_badge', '/user_badges'),
        ('admin.webhook', '/webhooks'),
    ]

    register_blueprints(app, blueprints)
