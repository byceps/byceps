"""
byceps.application.blueprints.blueprints
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Iterator, Optional, Tuple

from flask import Flask

from ..config import AppMode
from ..util.framework.blueprint import get_blueprint


BlueprintReg = Tuple[Flask, str, Optional[str]]


def register_blueprints(app: Flask, app_mode: AppMode) -> None:
    """Register blueprints depending on the configuration."""
    for parent, name, url_prefix in _get_blueprints(app, app_mode):
        blueprint = get_blueprint(name)
        parent.register_blueprint(blueprint, url_prefix=url_prefix)

    if app.config['API_ENABLED']:
        register_api_blueprints(app)


def _get_blueprints(app: Flask, app_mode: AppMode) -> Iterator[BlueprintReg]:
    """Yield blueprints to register on the application."""
    if app_mode.is_admin() or app_mode.is_site():
        yield from _get_blueprints_common(app)

    if app_mode.is_admin():
        yield from _get_blueprints_admin(app)
    elif app_mode.is_site():
        yield from _get_blueprints_site(app)

    yield (app, 'monitoring.healthcheck', '/health')

    if app.config['METRICS_ENABLED']:
        yield (app, 'monitoring.metrics', '/metrics')

    if app_mode.is_admin() or app_mode.is_site():
        if app.config.get('STYLE_GUIDE_ENABLED', False):
            yield (app, 'common.style_guide', '/style_guide')


def _get_blueprints_common(app: Flask) -> Iterator[BlueprintReg]:
    yield from [
        (app, 'common.authentication.password',  '/authentication/password' ),
        (app, 'common.core',                     None                       ),
        (app, 'common.guest_server',             None                       ),
        (app, 'common.locale',                   '/locale'                  ),
    ]


def _get_blueprints_site(app: Flask) -> Iterator[BlueprintReg]:
    yield from [
        (app, 'site.attendance',                 '/attendance'              ),
        (app, 'site.authentication.login',       '/authentication'          ),
        (app, 'site.board',                      '/board'                   ),
        (app, 'site.consent',                    '/consent'                 ),
        (app, 'site.core',                       '/'                        ),
        (app, 'site.dashboard',                  '/dashboard'               ),
        (app, 'site.guest_server',               '/guest_servers'           ),
        (app, 'site.news',                       '/news'                    ),
        (app, 'site.newsletter',                 '/newsletter'              ),
        (app, 'site.orga_team',                  '/orgas'                   ),
        (app, 'site.party_history',              '/party_history'           ),
        (app, 'site.seating',                    '/seating'                 ),
        (app, 'site.shop.order',                 '/shop'                    ),
        (app, 'site.shop.orders',                '/shop/orders'             ),
        (app, 'site.snippet',                    None                       ),
        (app, 'site.ticketing',                  '/tickets'                 ),
        (app, 'site.tourney',                    '/tourneys'                ),
        (app, 'site.user.avatar',                '/users'                   ),
        (app, 'site.user.creation',              '/users'                   ),
        (app, 'site.user.current',               '/users'                   ),
        (app, 'site.user.settings',              '/users/me/settings'       ),
        (app, 'site.user.email_address',         '/users/email_address'     ),
        (app, 'site.user_profile',               '/users'                   ),
        (app, 'site.user_badge',                 '/user_badges'             ),
        (app, 'site.user_group',                 '/user_groups'             ),
        (app, 'site.user_message',               '/user_messages'           ),
    ]


def _get_blueprints_admin(app: Flask) -> Iterator[BlueprintReg]:
    yield from [
        (app, 'admin.api',                       '/admin/api'               ),
        (app, 'admin.attendance',                '/admin/attendance'        ),
        (app, 'admin.authentication.login',      '/authentication'          ),
        (app, 'admin.authorization',             '/admin/authorization'     ),
        (app, 'admin.board',                     '/admin/boards'            ),
        (app, 'admin.brand',                     '/admin/brands'            ),
        (app, 'admin.consent',                   '/admin/consent'           ),
        (app, 'admin.core',                      '/'                        ),
        (app, 'admin.dashboard',                 '/admin/dashboard'         ),
        (app, 'admin.guest_server',              '/admin/guest_servers'     ),
        (app, 'admin.news',                      '/admin/news'              ),
        (app, 'admin.newsletter',                '/admin/newsletter'        ),
        (app, 'admin.jobs',                      '/admin/jobs'              ),
        (app, 'admin.maintenance',               '/admin/maintenance'       ),
        (app, 'admin.more',                      '/admin/more'              ),
        (app, 'admin.orga',                      '/admin/orgas'             ),
        (app, 'admin.orga_presence',             '/admin/presence'          ),
        (app, 'admin.orga_team',                 '/admin/orga_teams'        ),
        (app, 'admin.party',                     '/admin/parties'           ),
        (app, 'admin.seating',                   '/admin/seating'           ),
        (app, 'admin.shop',                      None                       ),
        (app, 'admin.shop.article',              '/admin/shop/articles'     ),
        (app, 'admin.shop.catalog',              '/admin/shop/catalogs'     ),
        (app, 'admin.shop.email',                '/admin/shop/email'        ),
        (app, 'admin.shop.order',                '/admin/shop/orders'       ),
        (app, 'admin.shop.shipping',             '/admin/shop/shipping'     ),
        (app, 'admin.shop.shop',                 '/admin/shop/shop'         ),
        (app, 'admin.shop.storefront',           '/admin/shop/storefronts'  ),
        (app, 'admin.site',                      '/admin/sites'             ),
        (app, 'admin.snippet',                   '/admin/snippets'          ),
        (app, 'admin.snippet.mountpoint',        '/admin/snippets/mountpoints'  ),
        (app, 'admin.ticketing',                 '/admin/ticketing'         ),
        (app, 'admin.ticketing.category',        '/admin/ticketing/categories'  ),
        (app, 'admin.ticketing.checkin',         '/admin/ticketing/checkin' ),
        (app, 'admin.tourney',                   None                       ),
        (app, 'admin.tourney.category',          '/admin/tourney/categories'),
        (app, 'admin.tourney.tourney',           '/admin/tourney/tourneys'  ),
        (app, 'admin.user',                      '/admin/users'             ),
        (app, 'admin.user_badge',                '/admin/user_badges'       ),
        (app, 'admin.webhook',                   '/admin/webhooks'          ),
    ]


def register_api_blueprints(app: Flask) -> None:
    api = get_blueprint('api')
    api_v1 = get_blueprint('api.v1')

    for name, url_prefix in [
        ('attendance',              '/attendances'          ),
        ('snippet',                 '/snippets'             ),
        ('tourney.avatar',          '/tourney/avatars'      ),
        ('tourney.match.comments',  '/tourney'              ),
        ('ticketing',               '/ticketing'            ),
        ('user',                    '/users'                ),
        ('user_avatar',             '/user_avatars'         ),
        ('user_badge',              '/user_badges'          ),
    ]:
        package = f'api.v1.{name}'
        blueprint = get_blueprint(package)
        api_v1.register_blueprint(blueprint, url_prefix=url_prefix)

    api.register_blueprint(api_v1, url_prefix='/v1')
    app.register_blueprint(api, url_prefix='/api')
