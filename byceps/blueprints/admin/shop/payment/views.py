"""
byceps.blueprints.admin.shop.payment.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.services.shop.payment import payment_gateway_service
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.templating import templated
from byceps.util.views import permission_required


blueprint = create_blueprint('shop_payment_admin', __name__)


@blueprint.get('')
@permission_required('shop.view')
@templated
def index():
    """List payment gateways."""
    payment_gateways = payment_gateway_service.get_all_payment_gateways()

    return {
        'payment_gateways': payment_gateways,
    }
