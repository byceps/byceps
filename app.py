"""
application instance
~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from warnings import warn

from byceps.application import create_app
from byceps.database import db
from byceps.services.brand.dbmodels.brand import Brand
from byceps.services.party.dbmodels.party import Party
from byceps.services.shop.article.dbmodels.article import DbArticle
from byceps.services.shop.order.dbmodels.line_item import LineItem
from byceps.services.shop.order.dbmodels.order import Order
from byceps.services.shop.order.service import find_order_by_order_number
from byceps.services.shop.order.transfer.order import (
    PaymentState as OrderPaymentState,
)
from byceps.services.ticketing.ticket_service import find_ticket_by_code
from byceps.services.user.dbmodels.detail import UserDetail
from byceps.services.user.dbmodels.user import User
from byceps.services.user.service import find_db_user_by_screen_name


app = create_app()


if (
    app.env == 'development'
    and app.debug
    and app.config.get('DEBUG_TOOLBAR_ENABLED', False)
):
    try:
        from flask_debugtoolbar import DebugToolbarExtension
    except ImportError:
        warn(
            'Could not import Flask-DebugToolbar. '
            '`pip install Flask-DebugToolbar` should make it available.'
        )
    else:
        app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
        toolbar = DebugToolbarExtension(app)


@app.shell_context_processor
def extend_shell_context():
    """Provide common objects to make available in the application shell."""
    return {
        'app': app,
        'db': db,
        'DbArticle': DbArticle,
        'Brand': Brand,
        'find_order_by_order_number': find_order_by_order_number,
        'Order': Order,
        'LineItem': LineItem,
        'OrderPaymentState': OrderPaymentState,
        'Party': Party,
        'find_ticket_by_code': find_ticket_by_code,
        'User': User,
        'UserDetail': UserDetail,
        'find_db_user_by_screen_name': find_db_user_by_screen_name,
    }
