#!/usr/bin/env python
"""
management script
~~~~~~~~~~~~~~~~~

Run the application, take administrative action.

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from werkzeug.wsgi import SharedDataMiddleware

from byceps.application import create_app, init_app
from byceps.config import STATIC_URL_PREFIX_BRAND, STATIC_URL_PREFIX_GLOBAL, \
    STATIC_URL_PREFIX_PARTY
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


if __name__ == '__main__':
    app.run()
