"""
byceps.application.blueprints.site
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import Flask

from byceps.util.framework.blueprint import register_blueprints

from .common import get_common_blueprints


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
            'services.external_accounts.discord.blueprints.site',
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
        ('services.shop.order.blueprints.site', '/shop'),
        ('services.shop.orders.blueprints.site', '/shop/orders'),
        (
            'services.shop.payment.paypal.blueprints.site',
            '/shop/payment/paypal',
        ),
        (
            'services.shop.payment.stripe.blueprints.site',
            '/shop/payment/stripe',
        ),
        ('services.site.blueprints.site', None),
        ('services.snippet.blueprints.site', None),
        ('services.ticketing.blueprints.site', '/tickets'),
        ('services.timetable.blueprints.site', '/timetable'),
        ('services.tourney.blueprints.site', '/tourneys'),
        ('services.user.avatar.blueprints.site', '/users'),
        ('services.user.creation.blueprints.site', '/users'),
        ('services.user.current.blueprints.site', '/users'),
        ('services.user.email_address.blueprints.site', '/users/email_address'),
        ('services.user.settings.blueprints.site', '/users/me/settings'),
        ('services.user_badge.blueprints.site', '/user_badges'),
        ('services.user_group.blueprints.site', '/user_groups'),
        ('services.user_message.blueprints.site', '/user_messages'),
        ('services.user_profile.blueprints.site', '/users'),
    ]

    register_blueprints(app, blueprints)
