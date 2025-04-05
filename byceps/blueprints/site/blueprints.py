"""
byceps.application.blueprints.site.blueprints
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import Flask

from byceps.blueprints.common.blueprints import get_common_blueprints
from byceps.util.framework.blueprint import register_blueprints


def register_site_blueprints(
    app: Flask, *, style_guide_enabled: bool = False
) -> None:
    common_blueprints = get_common_blueprints(
        style_guide_enabled=style_guide_enabled
    )

    blueprints = common_blueprints + [
        ('services.attendance.blueprints.site', '/attendance'),
        ('services.authn.login.blueprints.site', '/authentication'),
        ('services.board.blueprints.site', '/board'),
        (
            'services.external_accounts.blueprints.site.discord',
            '/connected_external_accounts/discord',
        ),
        ('services.consent.blueprints.site', '/consent'),
        ('services.core.blueprints.site', None),
        ('services.dashboard.blueprints.site', '/dashboard'),
        ('services.gallery.blueprints.site', '/galleries'),
        ('services.guest_server.blueprints.site', '/guest_servers'),
        ('services.homepage.blueprints.site', '/'),
        ('services.news.blueprints.site', '/news'),
        ('services.newsletter.blueprints.site', '/newsletter'),
        ('services.orga_team.blueprints.site', '/orgas'),
        ('services.page.blueprints.site', None),
        ('services.party_history.blueprints.site', '/party_history'),
        ('services.seating.blueprints.site', '/seating'),
        ('blueprints.site.shop.order', '/shop'),
        ('blueprints.site.shop.orders', '/shop/orders'),
        ('blueprints.site.shop.payment.paypal', '/shop/payment/paypal'),
        ('blueprints.site.shop.payment.stripe', '/shop/payment/stripe'),
        ('services.site.blueprints.site', None),
        ('services.snippet.blueprints.site', None),
        ('services.ticketing.blueprints.site', '/tickets'),
        ('services.timetable.blueprints.site', '/timetable'),
        ('services.tourney.blueprints.site', '/tourneys'),
        ('blueprints.site.user.avatar', '/users'),
        ('blueprints.site.user.creation', '/users'),
        ('blueprints.site.user.current', '/users'),
        ('blueprints.site.user.settings', '/users/me/settings'),
        ('blueprints.site.user.email_address', '/users/email_address'),
        ('blueprints.site.user_profile', '/users'),
        ('blueprints.site.user_badge', '/user_badges'),
        ('blueprints.site.user_group', '/user_groups'),
        ('blueprints.site.user_message', '/user_messages'),
    ]

    register_blueprints(app, blueprints)
