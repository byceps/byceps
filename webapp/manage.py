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
from byceps.database import db


ENVIRONMENT = 'development'


app = create_app(ENVIRONMENT, initialize=True)

if app.debug:
    exports = {
        '/users/avatars': str(app.config['PATH_USER_AVATAR_IMAGES']),
    }
    app.wsgi_app = SharedDataMiddleware(app.wsgi_app, exports)

manager = Manager(app)


@manager.shell
def make_shell_context():
    return {
        'app': app,
        'db': db,
    }


if __name__ == '__main__':
    manager.run()
