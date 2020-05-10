"""
byceps.blueprints.admin.shop.storefront.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import abort

from .....services.shop.sequence import service as sequence_service
from .....services.shop.shop import service as shop_service
from .....services.shop.storefront import service as storefront_service
from .....util.framework.blueprint import create_blueprint
from .....util.framework.templating import templated

from ....authorization.decorators import permission_required

from ..shop.authorization import ShopPermission


blueprint = create_blueprint('shop_storefront_admin', __name__)


@blueprint.route('/for_shop/<shop_id>')
@permission_required(ShopPermission.view)
@templated
def index_for_shop(shop_id):
    """List storefronts for that shop."""
    shop = shop_service.find_shop(shop_id)
    if shop is None:
        abort(404)

    storefronts = storefront_service.get_storefronts_for_shop(shop.id)

    order_number_prefixes_by_sequence_id = _get_order_number_prefixes_by_sequence_id(
        storefronts, shop.id
    )

    return {
        'shop': shop,
        'storefronts': storefronts,
        'order_number_prefixes_by_sequence_id': order_number_prefixes_by_sequence_id,
    }


def _get_order_number_prefixes_by_sequence_id(storefronts, shop_id):
    sequence_ids = {sf.order_number_sequence_id for sf in storefronts}
    sequences = sequence_service.find_order_number_sequences_for_shop(shop_id)
    return {seq.id: seq.prefix for seq in sequences}


@blueprint.route('/<storefront_id>')
@permission_required(ShopPermission.view)
@templated
def view(storefront_id):
    """Show a single storefront."""
    storefront = storefront_service.find_storefront(storefront_id)
    if storefront is None:
        abort(404)

    shop = shop_service.get_shop(storefront.shop_id)

    order_number_prefix = sequence_service.find_order_number_sequence(
        storefront.order_number_sequence_id
    )

    return {
        'storefront': storefront,
        'shop': shop,
        'order_number_prefix': order_number_prefix,
    }
