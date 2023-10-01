"""
byceps.application.blueprints.admin.blueprints
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
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
        ('admin.api', '/admin/api'),
        ('admin.attendance', '/admin/attendance'),
        ('admin.authn.identity_tag', '/admin/authentication/identity_tags'),
        ('admin.authn.login', '/authentication'),
        ('admin.authz', '/admin/authorization'),
        ('admin.board', '/admin/boards'),
        ('admin.brand', '/admin/brands'),
        ('admin.consent', '/admin/consent'),
        ('admin.core', '/'),
        ('admin.dashboard', '/admin/dashboard'),
        ('admin.guest_server', '/admin/guest_servers'),
        ('admin.jobs', '/admin/jobs'),
        ('admin.language', '/admin/languages'),
        ('admin.maintenance', '/admin/maintenance'),
        ('admin.more', '/admin/more'),
        ('admin.news', '/admin/news'),
        ('admin.newsletter', '/admin/newsletter'),
        ('admin.orga', '/admin/orgas'),
        ('admin.orga_presence', '/admin/presence'),
        ('admin.orga_team', '/admin/orga_teams'),
        ('admin.page', '/admin/pages'),
        ('admin.party', '/admin/parties'),
        ('admin.seating', '/admin/seating'),
        ('admin.shop', None),
        ('admin.shop.article', '/admin/shop/articles'),
        ('admin.shop.catalog', '/admin/shop/catalogs'),
        ('admin.shop.email', '/admin/shop/email'),
        ('admin.shop.order', '/admin/shop/orders'),
        ('admin.shop.cancelation_request', '/admin/shop/cancelation_requests'),
        ('admin.shop.shipping', '/admin/shop/shipping'),
        ('admin.shop.shop', '/admin/shop/shop'),
        ('admin.shop.storefront', '/admin/shop/storefronts'),
        ('admin.site', '/admin/sites'),
        ('admin.site.navigation', '/admin/sites/navigation'),
        ('admin.snippet', '/admin/snippets'),
        ('admin.ticketing', '/admin/ticketing'),
        ('admin.ticketing.category', '/admin/ticketing/categories'),
        ('admin.ticketing.checkin', '/admin/ticketing/checkin'),
        ('admin.tourney', None),
        ('admin.tourney.category', '/admin/tourney/categories'),
        ('admin.tourney.tourney', '/admin/tourney/tourneys'),
        ('admin.user', '/admin/users'),
        ('admin.user_badge', '/admin/user_badges'),
        ('admin.webhook', '/admin/webhooks'),
    ]

    register_blueprints(app, blueprints)
