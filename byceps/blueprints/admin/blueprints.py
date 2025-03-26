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
            'services.authn.identity_tag.blueprints.admin',
            '/authentication/identity_tags',
        ),
        ('services.authn.login.blueprints.admin', '/authentication'),
        ('services.authz.blueprints.admin', '/authorization'),
        ('services.board.blueprints.admin', '/boards'),
        ('services.brand.blueprints.admin', '/brands'),
        ('services.consent.blueprints.admin', '/consent'),
        ('services.core.blueprints.admin', '/'),
        ('services.dashboard.blueprints.admin', '/dashboard'),
        ('services.demo_data.blueprints.admin', '/demo_data'),
        ('services.gallery.blueprints.admin', '/galleries'),
        ('services.guest_server.blueprints.admin', '/guest_servers'),
        ('services.jobs.blueprints.admin', '/jobs'),
        ('services.language.blueprints.admin', '/languages'),
        ('services.maintenance.blueprints.admin', '/maintenance'),
        ('blueprints.admin.more', '/more'),
        ('services.news.blueprints.admin', '/news'),
        ('services.newsletter.blueprints.admin', '/newsletter'),
        ('services.orga.blueprints.admin', '/orgas'),
        ('services.orga_presence.blueprints.admin', '/presence'),
        ('services.orga_team.blueprints.admin', '/orga_teams'),
        ('services.page.blueprints.admin', '/pages'),
        ('services.party.blueprints.admin', '/parties'),
        ('services.seating.blueprints.admin', '/seating'),
        ('services.shop.blueprints.admin', None),
        (
            'services.shop.cancellation_request.blueprints.admin',
            '/shop/cancellation_requests',
        ),
        ('services.shop.catalog.blueprints.admin', '/shop/catalogs'),
        ('services.shop.email.blueprints.admin', '/shop/email'),
        ('services.shop.order.blueprints.admin', '/shop/orders'),
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
