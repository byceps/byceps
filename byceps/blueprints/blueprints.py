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

from byceps.util.framework.blueprint import BlueprintReg, register_blueprints


log = structlog.get_logger()


def register_admin_blueprints(app: Flask) -> None:
    blueprints = _get_admin_blueprints(app)
    register_blueprints(app, blueprints)
    log.info('Admin blueprints: enabled')


def register_site_blueprints(app: Flask) -> None:
    blueprints = _get_site_blueprints(app)
    register_blueprints(app, blueprints)
    log.info('Site blueprints: enabled')


def _get_admin_blueprints(app: Flask) -> Iterator[BlueprintReg]:
    """Yield blueprints to register on the application."""
    yield from _get_blueprints_common(app)

    yield from [
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


def _get_site_blueprints(app: Flask) -> Iterator[BlueprintReg]:
    """Yield blueprints to register on the application."""
    yield from _get_blueprints_common(app)

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


def _get_blueprints_common(app: Flask) -> Iterator[BlueprintReg]:
    yield from [
        ('common.authn.password', '/authentication/password'),
        ('common.core', None),
        ('common.guest_server', None),
        ('common.locale', '/locale'),
    ]

    yield ('monitoring.healthcheck', '/health')

    if app.config.get('STYLE_GUIDE_ENABLED', False):
        yield ('common.style_guide', '/style_guide')
        log.info('Style guide: enabled')
    else:
        log.info('Style guide: disabled')
