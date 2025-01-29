"""
byceps.blueprints.site.shop.payment.mollie.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from mollie.api.client import Client
from mollie.api.error import Error
import structlog

from byceps.util.framework.blueprint import create_blueprint


log = structlog.get_logger()


blueprint = create_blueprint('shop_payment_mollie', __name__)
