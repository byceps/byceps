#!/usr/bin/env python
"""
management script
~~~~~~~~~~~~~~~~~

Run the application, take administrative action.

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import ssl

from flask_script import Manager
from flask_script.commands import Server
from werkzeug.wsgi import SharedDataMiddleware

from byceps.application import create_app, init_app
from byceps.config import STATIC_URL_PREFIX_BRAND, STATIC_URL_PREFIX_GLOBAL, \
    STATIC_URL_PREFIX_PARTY
from byceps.database import db
from byceps.services.brand.models import Brand
from byceps.services.party.models import Party
from byceps.services.shop.article.models.article import Article
from byceps.services.shop.order.models.order import Order, \
    PaymentState as OrderPaymentState
from byceps.services.shop.order.models.order_item import OrderItem
from byceps.services.user.models.detail import UserDetail
from byceps.services.user.models.user import User
from byceps.services.user.service import find_user_by_screen_name
from byceps.util.system import get_config_filename_from_env_or_exit


config_filename = get_config_filename_from_env_or_exit()

app = create_app(config_filename)
init_app(app)


def _assemble_exports():
    exports = {}

    _export_path_if_configured(exports, 'PATH_GLOBAL', STATIC_URL_PREFIX_GLOBAL)
    _export_path_if_configured(exports, 'PATH_BRAND', STATIC_URL_PREFIX_BRAND)
    _export_path_if_configured(exports, 'PATH_PARTY', STATIC_URL_PREFIX_PARTY)

    return exports


def _export_path_if_configured(exports, config_key, url_path):
    path = app.config.get(config_key)
    if path:
        exports[url_path] = str(path)


if app.debug:
    exports = _assemble_exports()
    app.wsgi_app = SharedDataMiddleware(app.wsgi_app, exports)

    from flask_debugtoolbar import DebugToolbarExtension
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    toolbar = DebugToolbarExtension(app)

manager = Manager(app)


class SslServer(Server):

    def __init__(self, **kwargs):
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        ssl_context.load_cert_chain(
            'keys/development.cert',
            'keys/development.key')
        kwargs['ssl_context'] = ssl_context

        super().__init__(**kwargs)


manager.add_command('runserver_ssl', SslServer())


@manager.shell
def make_shell_context():
    return {
        'app': app,
        'db': db,
        'Article': Article,
        'Brand': Brand,
        'Order': Order,
        'OrderItem': OrderItem,
        'OrderPaymentState': OrderPaymentState,
        'Party': Party,
        'User': User,
        'UserDetail': UserDetail,
        'find_user_by_screen_name': find_user_by_screen_name,
    }


if __name__ == '__main__':
    manager.run()
