"""
byceps.services.shop.sold_products.blueprints.admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, request
from sqlalchemy.exc import NoResultFound

from byceps.services.party import party_service
from byceps.services.party.models import Party
from byceps.services.shop.order import sold_products_service
from byceps.services.shop.product import product_service
from byceps.services.shop.product.models import Product, ProductNumber
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.templating import templated
from byceps.util.views import permission_required, textified


from .forms import GenerateForm


blueprint = create_blueprint('shop_sold_products_admin', __name__)


@blueprint.get('/for_party/<party_id>')
@permission_required('shop_order.view')
@templated
def index(party_id):
    """Show form to list paid orders of select products with quantities."""
    party = _get_party_or_404(party_id)

    form = GenerateForm()

    return {
        'party': party,
        'form': form,
    }


@blueprint.get('/for_party/<party_id>/report')
@permission_required('shop_order.view')
@templated
def view(party_id):
    """List paid orders of select products with quantities."""
    party = _get_party_or_404(party_id)

    form = GenerateForm(request.args)
    if not form.validate():
        abort(400, 'No product numbers specified.')

    product_number1 = form.product_number1.data
    product_number2 = form.product_number2.data
    product_number3 = form.product_number3.data
    product_number4 = form.product_number4.data

    product_numbers = [
        product_number1,
        product_number2,
        product_number3,
        product_number4,
    ]

    report = _assemble_report(party, product_numbers)

    return {
        'party': party,
        'product_number1': product_number1,
        'product_number2': product_number2,
        'product_number3': product_number3,
        'product_number4': product_number4,
        'report': report,
    }


@blueprint.get('/for_party/<party_id>/report_as_csv')
@permission_required('shop_order.view')
@textified
def export_as_csv(party_id):
    """List paid orders of select products with quantities, as CSV."""
    party = _get_party_or_404(party_id)

    form = GenerateForm(request.args)
    if not form.validate():
        abort(400, 'No product numbers specified.')

    product_number1 = form.product_number1.data
    product_number2 = form.product_number2.data
    product_number3 = form.product_number3.data
    product_number4 = form.product_number4.data

    product_numbers = [
        product_number1,
        product_number2,
        product_number3,
        product_number4,
    ]

    report = _assemble_report(party, product_numbers)

    return sold_products_service.export_sold_products_as_csv(report)


def _assemble_report(party: Party, product_numbers: list[str]):
    products = [
        _get_product_number(product_number)
        for product_number in product_numbers
        if product_number
    ]

    return sold_products_service.get_sold_products_report(party, products)


# -------------------------------------------------------------------- #
# helpers


def _get_party_or_404(party_id):
    party = party_service.find_party(party_id)

    if party is None:
        abort(404)

    return party


def _get_product_number(product_number: str) -> Product:
    """Validate product number, return corresponding product."""
    try:
        return product_service.get_product_by_number(
            ProductNumber(product_number)
        )
    except NoResultFound:
        abort(400, f'Unknown product number "{product_number}"')
