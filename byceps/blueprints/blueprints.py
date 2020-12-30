"""
byceps.application.blueprints.blueprints
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Iterator, Optional, Tuple

from flask import Flask

from .. import config
from ..util.framework.blueprint import register_blueprint


BlueprintReg = Tuple[str, Optional[str]]


def register_blueprints(app: Flask) -> None:
    """Register blueprints depending on the configuration."""
    for name, url_prefix in _get_blueprints(app):
        register_blueprint(app, name, url_prefix)


def _get_blueprints(app: Flask) -> Iterator[BlueprintReg]:
    """Yield blueprints to register on the application."""
    yield from _get_blueprints_common()

    current_mode = config.get_app_mode(app)
    if current_mode.is_site():
        yield from _get_blueprints_site()
    elif current_mode.is_admin():
        yield from _get_blueprints_admin()

    yield from _get_blueprints_api()

    yield from _get_blueprints_monitoring(app.config)

    if app.debug:
        yield from _get_blueprints_debug()


def _get_blueprints_common() -> Iterator[BlueprintReg]:
    yield from [
        ('common.authentication',           '/authentication'           ),
        ('common.authentication.password',  '/authentication/password'  ),
        ('common.authorization',            None                        ),
        ('common.core',                     '/core'                     ),
        ('common.user',                     None                        ),
        ('common.user.avatar',              '/users'                    ),
        ('common.user.creation',            '/users'                    ),
        ('common.user.current',             '/users'                    ),
        ('common.user.email_address',       '/users/email_address'      ),
        ('common.user.settings',            '/users/me/settings'        ),
    ]


def _get_blueprints_site() -> Iterator[BlueprintReg]:
    yield from [
        ('site.attendance',                 '/attendance'               ),
        ('site.board',                      '/board'                    ),
        ('site.consent',                    '/consent'                  ),
        ('site.news',                       '/news'                     ),
        ('site.newsletter',                 '/newsletter'               ),
        ('site.orga_team',                  '/orgas'                    ),
        ('site.party',                      None                        ),
        ('site.seating',                    '/seating'                  ),
        ('site.shop.order',                 '/shop'                     ),
        ('site.shop.orders',                '/shop/orders'              ),
        ('site.snippet',                    None                        ),
        ('site.terms',                      '/terms'                    ),
        ('site.ticketing',                  '/tickets'                  ),
        ('site.tourney',                    '/tourneys'                 ),
        ('site.user.profile',               '/users'                    ),
        ('site.user_badge',                 '/user_badges'              ),
        ('site.user_group',                 '/user_groups'              ),
        ('site.user_message',               '/user_messages'            ),
    ]


def _get_blueprints_admin() -> Iterator[BlueprintReg]:
    yield from [
        ('admin.attendance',                '/admin/attendance'         ),
        ('admin.authorization',             '/admin/authorization'      ),
        ('admin.board',                     '/admin/boards'             ),
        ('admin.brand',                     '/admin/brands'             ),
        ('admin.consent',                   '/admin/consent'            ),
        ('admin.core',                      None                        ),
        ('admin.dashboard',                 '/admin/dashboard'          ),
        ('admin.news',                      '/admin/news'               ),
        ('admin.newsletter',                '/admin/newsletter'         ),
        ('admin.jobs',                      '/admin/jobs'               ),
        ('admin.more',                      '/admin/more'               ),
        ('admin.orga',                      '/admin/orgas'              ),
        ('admin.orga_presence',             '/admin/presence'           ),
        ('admin.orga_team',                 '/admin/orga_teams'         ),
        ('admin.party',                     '/admin/parties'            ),
        ('admin.seating',                   '/admin/seating'            ),
        ('admin.shop',                      None                        ),
        ('admin.shop.article',              '/admin/shop/articles'      ),
        ('admin.shop.email',                '/admin/shop/email'         ),
        ('admin.shop.order',                '/admin/shop/orders'        ),
        ('admin.shop.shipping',             '/admin/shop/shipping'      ),
        ('admin.shop.shop',                 '/admin/shop/shop'          ),
        ('admin.shop.storefront',           '/admin/shop/storefronts'   ),
        ('admin.site',                      '/admin/sites'              ),
        ('admin.snippet',                   '/admin/snippets'           ),
        ('admin.terms',                     '/admin/terms'              ),
        ('admin.ticketing',                 '/admin/ticketing'          ),
        ('admin.ticketing.checkin',         '/admin/ticketing/checkin'  ),
        ('admin.tourney',                   '/admin/tourney'            ),
        ('admin.user',                      '/admin/users'              ),
        ('admin.user_badge',                '/admin/user_badges'        ),
        ('admin.webhook',                   '/admin/webhooks'           ),
    ]


def _get_blueprints_api() -> Iterator[BlueprintReg]:
    yield from [
        ('api.v1.attendance',               '/api/v1/attendances'       ),
        ('api.v1.snippet',                  '/api/v1/snippets'          ),
        ('api.v1.tourney.avatar',           '/api/v1/tourney/avatars'   ),
        ('api.v1.tourney.match.comments',   '/api/v1/tourney'           ),
        ('api.v1.user',                     '/api/v1/users'             ),
        ('api.v1.user_avatar',              '/api/v1/user_avatars'      ),
        ('api.v1.user_badge',               '/api/v1/user_badges'       ),
    ]


def _get_blueprints_monitoring(app_config) -> Iterator[BlueprintReg]:
    yield from [
        ('monitoring.healthcheck',      '/health'                   ),
    ]

    if app_config['METRICS_ENABLED']:
        yield from [
            ('monitoring.metrics',          '/metrics'                  ),
        ]


def _get_blueprints_debug() -> Iterator[BlueprintReg]:
    yield from [
        ('common.style_guide',              '/style_guide'              ),
    ]
