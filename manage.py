#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
management script
~~~~~~~~~~~~~~~~~

Run the application, take administrative action.

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import ssl

from flask.ext.script import Manager
from flask.ext.script.commands import Server
from werkzeug.wsgi import SharedDataMiddleware

from byceps.application import create_app, init_app
from byceps.blueprints.brand.models import Brand
from byceps.blueprints.party.models import Party
from byceps.blueprints.shop.models.article import Article
from byceps.blueprints.shop.models.order import Order, OrderItem, \
    PaymentState as OrderPaymentState
from byceps.blueprints.user.models.detail import UserDetail
from byceps.blueprints.user.models.user import User
from byceps.database import db
from byceps.util.system import get_config_env_name_from_env


environment = get_config_env_name_from_env(default='development')

app = create_app(environment)
init_app(app)


def _assemble_exports():
    exports = {
        '/users/avatars': str(app.config['PATH_USER_AVATAR_IMAGES']),
    }

    _export_path_if_configured(exports, 'PATH_GLOBAL', '/global')
    _export_path_if_configured(exports, 'PATH_BRAND', '/brand')
    _export_path_if_configured(exports, 'PATH_PARTY', '/party')

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
    }


if __name__ == '__main__':
    manager.run()
