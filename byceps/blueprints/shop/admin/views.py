"""
byceps.blueprints.shop.admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import abort

from ....services.party import service as party_service
from ....services.shop.sequence import service as sequence_service
from ....services.shop.shop import service as shop_service
from ....util.framework.blueprint import create_blueprint
from ....util.framework.templating import templated

from ...authorization.decorators import permission_required
from ...authorization.registry import permission_registry

from .authorization import ShopPermission


blueprint = create_blueprint('shop_admin', __name__)


permission_registry.register_enum(ShopPermission)


@blueprint.route('/for_party/<party_id>')
@permission_required(ShopPermission.view)
@templated
def view_for_party(party_id):
    """Show the shop for that party."""
    party = _get_party_or_404(party_id)
    shop = shop_service.find_shop_for_party(party.id)

    if shop is None:
        return {
            'party': party,
        }

    article_number_sequence = sequence_service \
        .find_article_number_sequence(shop.id)

    order_number_sequence = sequence_service.find_order_number_sequence(shop.id)

    return {
        'party': party,
        'shop': shop,
        'article_number_sequence': article_number_sequence,
        'order_number_sequence': order_number_sequence,
    }


def _get_party_or_404(party_id):
    party = party_service.find_party(party_id)

    if party is None:
        abort(404)

    return party
