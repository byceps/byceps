"""
application instance
~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from pathlib import Path

from werkzeug.wsgi import SharedDataMiddleware

from byceps.application import create_app, init_app
from byceps import config
from byceps.database import db
from byceps.services.brand.models.brand import Brand
from byceps.services.party.models.party import Party
from byceps.services.shop.article.models.article import Article
from byceps.services.shop.order.models.order import Order
from byceps.services.shop.order.models.order_item import OrderItem
from byceps.services.shop.order.service import find_order_by_order_number
from byceps.services.shop.order.transfer.models import \
    PaymentState as OrderPaymentState
from byceps.services.ticketing.ticket_service import find_ticket_by_code
from byceps.services.user.models.detail import UserDetail
from byceps.services.user.models.user import User
from byceps.services.user.service import find_user_by_screen_name
from byceps.util.system import get_config_filename_from_env_or_exit


config_filename = get_config_filename_from_env_or_exit()

app = create_app(config_filename)
init_app(app)


def _generate_static_files_exports():
    """Yield static files exports."""
    # global, brand-specific, and party-specific files
    for url_path, config_key in [
        ('/global', 'PATH_GLOBAL'),
        ('/brand', 'PATH_BRAND'),
        ('/party', 'PATH_PARTY'),
    ]:
        path = app.config.get(config_key)
        if path:
            yield url_path, str(path)

    # site-specific files
    if config.get_site_mode(app).is_public():
        site_id = config.get_current_site_id(app)
        site_files_path = Path('sites') / site_id / 'static'
        yield '/site', str(site_files_path)


if app.env == 'development':
    # Share static files.
    exports = dict(_generate_static_files_exports())
    app.wsgi_app = SharedDataMiddleware(app.wsgi_app, exports)

    if app.debug:
        # Enable debug toolbar.
        from flask_debugtoolbar import DebugToolbarExtension
        app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
        toolbar = DebugToolbarExtension(app)


@app.shell_context_processor
def extend_shell_context():
    """Provide common objects to make available in the application shell."""
    return {
        'app': app,
        'db': db,
        'Article': Article,
        'Brand': Brand,
        'find_order_by_order_number': find_order_by_order_number,
        'Order': Order,
        'OrderItem': OrderItem,
        'OrderPaymentState': OrderPaymentState,
        'Party': Party,
        'find_ticket_by_code': find_ticket_by_code,
        'User': User,
        'UserDetail': UserDetail,
        'find_user_by_screen_name': find_user_by_screen_name,
    }
