"""
byceps.application.blueprints.admin
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import Flask

from byceps.util.framework.blueprint import register_blueprints

from .common import get_common_blueprints


def register_admin_blueprints(
    app: Flask,
    *,
    metrics_enabled: bool = False,
    style_guide_enabled: bool = False,
) -> None:
    common_blueprints = get_common_blueprints(
        style_guide_enabled=style_guide_enabled
    )

    blueprints = common_blueprints + [
        ('services.api.blueprints.admin', '/api'),
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
        ('services.more.blueprints.admin', '/more'),
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
        ('services.shop.payment.blueprints.admin', '/shop/payment'),
        ('services.shop.product.blueprints.admin', '/shop/products'),
        ('services.shop.shipping.blueprints.admin', '/shop/shipping'),
        ('services.shop.shop.blueprints.admin', '/shop/shop'),
        ('services.shop.sold_products.blueprints.admin', '/shop/sold_products'),
        ('services.shop.storefront.blueprints.admin', '/shop/storefronts'),
        ('services.site.blueprints.admin', '/sites'),
        ('services.site.navigation.blueprints.admin', '/sites/navigation'),
        ('services.snippet.blueprints.admin', '/snippets'),
        ('services.ticketing.blueprints.admin', '/ticketing'),
        (
            'services.ticketing.category.blueprints.admin',
            '/ticketing/categories',
        ),
        ('services.ticketing.checkin.blueprints.admin', '/ticketing/checkin'),
        ('services.timetable.blueprints.admin', '/timetables'),
        ('services.tourney.blueprints.admin', None),
        ('services.tourney.category.blueprints.admin', '/tourney/categories'),
        ('services.tourney.tourney.blueprints.admin', '/tourney/tourneys'),
        ('services.user.blueprints.admin', '/users'),
        ('services.user_badge.blueprints.admin', '/user_badges'),
        ('services.webhooks.blueprints.admin', '/webhooks'),
        ('services.whereabouts.blueprints.admin', '/whereabouts'),
    ]

    if metrics_enabled:
        blueprints.append(('services.metrics.blueprints.metrics', '/metrics'))

    register_blueprints(app, blueprints)
