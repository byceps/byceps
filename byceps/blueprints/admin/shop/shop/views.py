"""
byceps.blueprints.admin.shop.shop.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from collections import defaultdict

from flask import abort, request

from .....services.shop.article import service as article_service
from .....services.shop.order import (
    action_service as order_action_service,
    service as order_service,
)
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
def view_for_shop(shop_id):
    """Show the shop."""
    shop = _get_shop_or_404(shop_id)

    order_counts_by_payment_state = order_service.count_orders_per_payment_state(
        shop.id
    )

    order_actions_by_article_number = _get_order_actions_by_article_number(
        shop.id
    )

    return {
        'shop': shop,

        'order_counts_by_payment_state': order_counts_by_payment_state,
        'PaymentState': PaymentState,

        'settings': shop.extra_settings,

        'order_actions_by_article_number': order_actions_by_article_number,
    }


def _get_order_actions_by_article_number(shop_id):
    actions = order_action_service.get_actions(shop_id)

    actions.sort(key=lambda a: a.payment_state.name, reverse=True)
    actions.sort(key=lambda a: a.article_number)

    actions_by_article_number = defaultdict(list)
    for action in actions:
        actions_by_article_number[action.article_number].append(action)

    return actions_by_article_number


@blueprint.route('/shops/create')
@permission_required(ShopPermission.create)
@templated
def create_form(erroneous_form=None):
    """Show form to create a shop."""
    form = erroneous_form if erroneous_form else CreateForm()
    form.set_email_config_choices()

    return {
        'form': form,
    }


@blueprint.route('/shops', methods=['POST'])
@permission_required(ShopPermission.create)
def create():
    """Create a shop."""
    form = CreateForm(request.form)
    form.set_email_config_choices()

    if not form.validate():
        return create_form(form)

    shop_id = form.id.data.strip().lower()
    title = form.title.data.strip()
    email_config_id = form.email_config_id.data

    shop = shop_service.create_shop(shop_id, title, email_config_id)

    flash_success(f'Der Shop "{shop.title}" wurde angelegt.')
    return redirect_to('.index')


def _get_shop_or_404(shop_id):
    shop = shop_service.find_shop(shop_id)

    if shop is None:
        abort(404)

    return shop
