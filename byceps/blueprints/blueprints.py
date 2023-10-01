"""
byceps.application.blueprints.blueprints
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from collections.abc import Iterator

from flask import Flask
import structlog

from byceps.blueprints.common.blueprints import register_common_blueprints
from byceps.util.framework.blueprint import BlueprintReg, register_blueprints


log = structlog.get_logger()


def register_site_blueprints(app: Flask) -> None:
    register_common_blueprints(app)

    blueprints = _get_site_blueprints(app)
    register_blueprints(app, blueprints)
    log.info('Site blueprints: enabled')


def _get_site_blueprints(app: Flask) -> Iterator[BlueprintReg]:
    """Yield blueprints to register on the application."""
    yield from [
        ('site.attendance', '/attendance'),
        ('site.authn.login', '/authentication'),
        ('site.board', '/board'),
        (
            'site.connected_external_accounts.discord',
            '/connected_external_accounts/discord',
        ),
        ('site.consent', '/consent'),
        ('site.core', None),
        ('site.dashboard', '/dashboard'),
        ('site.guest_server', '/guest_servers'),
        ('site.homepage', '/'),
        ('site.news', '/news'),
        ('site.newsletter', '/newsletter'),
        ('site.orga_team', '/orgas'),
        ('site.page', None),
        ('site.party_history', '/party_history'),
        ('site.seating', '/seating'),
        ('site.shop.order', '/shop'),
        ('site.shop.orders', '/shop/orders'),
        ('site.site', None),
        ('site.snippet', None),
        ('site.ticketing', '/tickets'),
        ('site.tourney', '/tourneys'),
        ('site.user.avatar', '/users'),
        ('site.user.creation', '/users'),
        ('site.user.current', '/users'),
        ('site.user.settings', '/users/me/settings'),
        ('site.user.email_address', '/users/email_address'),
        ('site.user_profile', '/users'),
        ('site.user_badge', '/user_badges'),
        ('site.user_group', '/user_groups'),
        ('site.user_message', '/user_messages'),
    ]
