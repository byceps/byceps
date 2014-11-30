#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
management script
~~~~~~~~~~~~~~~~~

Run the application, take administrative action.

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from flask.ext.script import Manager
from werkzeug.wsgi import SharedDataMiddleware

from byceps.application import create_app
from byceps.blueprints.brand.models import Brand
from byceps.blueprints.party.models import Party
from byceps.blueprints.shop.models import Article, Order, OrderItem, \
    PaymentState as OrderPaymentState
from byceps.blueprints.user.models import User, UserDetail
from byceps.database import db
from byceps.util.money import EuroAmount
from byceps.util.system import get_config_env_name_from_env


environment = get_config_env_name_from_env(default='development')
app = create_app(environment, initialize=True)

if app.debug:
    exports = {
        '/content': str(app.config['PATH_CONTENT']),
        '/users/avatars': str(app.config['PATH_USER_AVATAR_IMAGES']),
    }
    app.wsgi_app = SharedDataMiddleware(app.wsgi_app, exports)

manager = Manager(app)


@manager.shell
def make_shell_context():
    return {
        'app': app,
        'db': db,
        'Article': Article,
        'Brand': Brand,
        'EuroAmount': EuroAmount,
        'Order': Order,
        'OrderItem': OrderItem,
        'OrderPaymentState': OrderPaymentState,
        'Party': Party,
        'User': User,
        'UserDetail': UserDetail,
    }


if __name__ == '__main__':
    manager.run()
