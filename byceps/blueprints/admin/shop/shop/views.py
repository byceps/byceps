"""
byceps.blueprints.admin.shop.shop.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, request

from .....services.brand import service as brand_service
from .....services.shop.order import service as order_service
from .....services.shop.order.transfer.models import PaymentState
from .....services.shop.shop import service as shop_service
from .....util.framework.blueprint import create_blueprint
from .....util.framework.flash import flash_success
from .....util.framework.templating import templated
from .....util.views import redirect_to

from ....common.authorization.decorators import permission_required
from ....common.authorization.registry import permission_registry

from .authorization import ShopPermission
from .forms import CreateForm


blueprint = create_blueprint('shop_shop_admin', __name__)


permission_registry.register_enum(ShopPermission)


@blueprint.route('/')
@permission_required(ShopPermission.view)
@templated
def index():
    """List all shops."""
    shops = shop_service.get_all_shops()

    return {
        'shops': shops,
    }


@blueprint.route('/for_shop/<shop_id>')
@permission_required(ShopPermission.view)
@templated
def view(shop_id):
    """Show the shop."""
    shop = _get_shop_or_404(shop_id)

    brand = brand_service.get_brand(shop.brand_id)

    order_counts_by_payment_state = order_service.count_orders_per_payment_state(
        shop.id
    )

    return {
        'shop': shop,
        'brand': brand,

        'order_counts_by_payment_state': order_counts_by_payment_state,
        'PaymentState': PaymentState,

        'settings': shop.extra_settings,
    }


@blueprint.route('/for_brand/<brand_id>')
def view_for_brand(brand_id):
    shop = shop_service.find_shop_for_brand(brand_id)

    if shop is None:
        abort(404)

    return redirect_to('.view', shop_id=shop.id)


@blueprint.route('/shops/create')
@permission_required(ShopPermission.create)
@templated
def create_form(erroneous_form=None):
    """Show form to create a shop."""
    form = erroneous_form if erroneous_form else CreateForm()
    form.set_brand_choices()

    return {
        'form': form,
    }


@blueprint.route('/shops', methods=['POST'])
@permission_required(ShopPermission.create)
def create():
    """Create a shop."""
    form = CreateForm(request.form)
    form.set_brand_choices()

    if not form.validate():
        return create_form(form)

    shop_id = form.id.data.strip().lower()
    brand_id = form.brand_id.data
    title = form.title.data.strip()

    shop = shop_service.create_shop(shop_id, brand_id, title)

    flash_success(f'Der Shop "{shop.title}" wurde angelegt.')
    return redirect_to('.index')


def _get_shop_or_404(shop_id):
    shop = shop_service.find_shop(shop_id)

    if shop is None:
        abort(404)

    return shop
