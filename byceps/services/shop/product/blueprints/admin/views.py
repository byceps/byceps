"""
byceps.services.shop.product.blueprints.admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import dataclasses
from datetime import date, datetime, time
from decimal import Decimal

from flask import abort, request
from flask_babel import gettext, to_user_timezone, to_utc
from moneyed import Money

from byceps.services.brand import brand_service
from byceps.services.party import party_service
from byceps.services.shop.order import (
    order_action_registry_service,
    order_action_service,
    ordered_products_service,
)
from byceps.services.shop.order.models.order import Order, PaymentState
from byceps.services.shop.product import (
    product_domain_service,
    product_sequence_service,
    product_service,
)
from byceps.services.shop.product.dbmodels.product import DbProduct
from byceps.services.shop.product.models import (
    Product,
    ProductNumber,
    ProductNumberSequence,
    ProductType,
    ProductWithQuantity,
    get_product_type_label,
)
from byceps.services.shop.shop import shop_service
from byceps.services.shop.shop.models import ShopID
from byceps.services.ticketing import ticket_category_service
from byceps.services.user_badge import user_badge_service
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.flash import flash_error, flash_success
from byceps.util.framework.templating import templated
from byceps.util.views import (
    permission_required,
    redirect_to,
    respond_no_content,
)

from .forms import (
    ProductAttachmentCreateForm,
    ProductCreateForm,
    ProductNumberSequenceCreateForm,
    ProductUpdateForm,
    RegisterBadgeAwardingActionForm,
    RegisterTicketBundlesCreationActionForm,
    RegisterTicketsCreationActionForm,
    TicketProductCreateForm,
    TicketBundleProductCreateForm,
)


blueprint = create_blueprint('shop_product_admin', __name__)


TAX_RATE_DISPLAY_FACTOR = Decimal('100')


@blueprint.get('/for_shop/<shop_id>', defaults={'page': 1})
@blueprint.get('/for_shop/<shop_id>/pages/<int:page>')
@permission_required('shop_product.view')
@templated
def index_for_shop(shop_id, page):
    """List products for that shop."""
    shop = _get_shop_or_404(shop_id)

    brand = brand_service.get_brand(shop.brand_id)

    per_page = request.args.get('per_page', type=int, default=15)

    search_term = request.args.get('search_term', default='').strip()

    db_products = product_service.get_products_for_shop_paginated(
        shop.id,
        page,
        per_page,
        search_term=search_term,
    )

    # Inherit order of enum members.
    product_type_labels_by_type = {
        type_: get_product_type_label(type_) for type_ in ProductType
    }

    totals_by_product_number = {
        db_product.item_number: ordered_products_service.count_ordered_products(
            db_product.id
        )
        for db_product in db_products.items
    }

    return {
        'shop': shop,
        'brand': brand,
        'products': db_products,
        'product_type_labels_by_type': product_type_labels_by_type,
        'totals_by_product_number': totals_by_product_number,
        'PaymentState': PaymentState,
        'per_page': per_page,
        'search_term': search_term,
    }


@blueprint.get('/<uuid:product_id>')
@permission_required('shop_product.view')
@templated
def view(product_id):
    """Show a single product."""
    db_product = product_service.find_product_with_details(product_id)
    if db_product is None:
        abort(404)

    shop = shop_service.get_shop(db_product.shop_id)

    brand = brand_service.get_brand(shop.brand_id)

    price_including_attached_products = _calculate_total_amount(db_product)

    type_label = get_product_type_label(db_product.type_)

    if db_product.type_ in (ProductType.ticket, ProductType.ticket_bundle):
        ticket_category = ticket_category_service.find_category(
            db_product.type_params['ticket_category_id']
        )
        if ticket_category is not None:
            ticket_party = party_service.get_party(ticket_category.party_id)
        else:
            ticket_party = None
    else:
        ticket_party = None
        ticket_category = None

    quantities = ordered_products_service.count_ordered_products(db_product.id)
    quantity_ordered = quantities[PaymentState.open]
    quantity_paid = quantities[PaymentState.paid]

    images = product_service.get_images_for_product(db_product.id)

    actions = order_action_service.get_actions_for_product(db_product.id)
    actions.sort(key=lambda a: a.payment_state.name, reverse=True)

    return {
        'product': db_product,
        'shop': shop,
        'brand': brand,
        'price_including_attached_products': price_including_attached_products,
        'type_label': type_label,
        'ticket_category': ticket_category,
        'ticket_party': ticket_party,
        'quantity_ordered': quantity_ordered,
        'quantity_paid': quantity_paid,
        'images': images,
        'actions': actions,
    }


def _calculate_total_amount(db_product: DbProduct) -> Money:
    products_with_quantities = [
        ProductWithQuantity(db_product, 1),
    ] + [
        ProductWithQuantity(attached_product.product, attached_product.quantity)
        for attached_product in db_product.attached_products
    ]

    return product_domain_service.calculate_total_amount(
        products_with_quantities
    )


@blueprint.get('/<uuid:product_id>/orders')
@permission_required('shop_product.view')
@templated
def view_orders(product_id):
    """List the orders for this product, and the corresponding quantities."""
    product = _get_product_or_404(product_id)

    shop = shop_service.get_shop(product.shop_id)
    brand = brand_service.get_brand(shop.brand_id)

    orders = ordered_products_service.get_orders_including_product(product.id)

    def transform(order: Order) -> tuple[Order, int]:
        quantity = sum(
            line_item.quantity
            for line_item in order.line_items
            if line_item.product_id == product.id
        )

        return order, quantity

    orders_with_quantities = list(map(transform, orders))

    quantity_total = sum(quantity for _, quantity in orders_with_quantities)

    return {
        'product': product,
        'shop': shop,
        'brand': brand,
        'quantity_total': quantity_total,
        'orders_with_quantities': orders_with_quantities,
        'now': datetime.utcnow(),
    }


@blueprint.get('/<uuid:product_id>/purchases')
@permission_required('shop_product.view')
@templated
def view_purchases(product_id):
    """List the purchases for this product, and the corresponding quantities."""
    product = _get_product_or_404(product_id)

    shop = shop_service.get_shop(product.shop_id)
    brand = brand_service.get_brand(shop.brand_id)

    orders = ordered_products_service.get_orders_including_product(
        product.id, only_payment_state=PaymentState.paid
    )

    def transform(order: Order) -> tuple[Order, int]:
        quantity = sum(
            line_item.quantity
            for line_item in order.line_items
            if line_item.product_id == product.id
        )

        return order, quantity

    orders_with_quantities = list(map(transform, orders))

    quantity_total = sum(quantity for _, quantity in orders_with_quantities)

    return {
        'product': product,
        'shop': shop,
        'brand': brand,
        'quantity_total': quantity_total,
        'orders_with_quantities': orders_with_quantities,
        'now': datetime.utcnow(),
    }


# -------------------------------------------------------------------- #
# create


@blueprint.get('/for_shop/<shop_id>/create/<type_name>')
@permission_required('shop_product.administrate')
@templated
def create_form(shop_id, type_name, erroneous_form=None):
    """Show form to create a product."""
    shop = _get_shop_or_404(shop_id)
    type_ = _get_product_type_or_400(type_name)

    brand = brand_service.get_brand(shop.brand_id)

    product_number_sequences = _get_active_product_number_sequences_for_shop(
        shop.id
    )
    product_number_sequence_available = bool(product_number_sequences)

    form = (
        erroneous_form
        if erroneous_form
        else ProductCreateForm(
            shop.id, price_amount=Decimal('0.0'), tax_rate=Decimal('19.0')
        )
    )
    form.set_product_number_sequence_choices(product_number_sequences)

    return {
        'shop': shop,
        'brand': brand,
        'product_type_name': type_.name,
        'product_type_label': get_product_type_label(type_),
        'product_number_sequence_available': product_number_sequence_available,
        'form': form,
    }


@blueprint.get('/for_shop/<shop_id>/create/ticket')
@permission_required('shop_product.administrate')
@templated
def create_ticket_form(shop_id, erroneous_form=None):
    """Show form to create a ticket product."""
    shop = _get_shop_or_404(shop_id)
    type_ = ProductType.ticket

    brand = brand_service.get_brand(shop.brand_id)

    product_number_sequences = _get_active_product_number_sequences_for_shop(
        shop.id
    )
    product_number_sequence_available = bool(product_number_sequences)

    form = (
        erroneous_form
        if erroneous_form
        else TicketProductCreateForm(
            shop.id, price_amount=Decimal('0.0'), tax_rate=Decimal('19.0')
        )
    )
    form.set_product_number_sequence_choices(product_number_sequences)
    form.set_ticket_category_choices(brand.id)

    return {
        'shop': shop,
        'brand': brand,
        'product_type_name': type_.name,
        'product_type_label': get_product_type_label(type_),
        'product_number_sequence_available': product_number_sequence_available,
        'form': form,
    }


@blueprint.get('/for_shop/<shop_id>/create/ticket_bundle')
@permission_required('shop_product.administrate')
@templated
def create_ticket_bundle_form(shop_id, erroneous_form=None):
    """Show form to create a ticket bundle product."""
    shop = _get_shop_or_404(shop_id)
    type_ = ProductType.ticket_bundle

    brand = brand_service.get_brand(shop.brand_id)

    product_number_sequences = _get_active_product_number_sequences_for_shop(
        shop.id
    )
    product_number_sequence_available = bool(product_number_sequences)

    form = (
        erroneous_form
        if erroneous_form
        else TicketBundleProductCreateForm(
            shop.id, price_amount=Decimal('0.0'), tax_rate=Decimal('19.0')
        )
    )
    form.set_product_number_sequence_choices(product_number_sequences)
    form.set_ticket_category_choices(brand.id)

    return {
        'shop': shop,
        'brand': brand,
        'product_type_name': type_.name,
        'product_type_label': get_product_type_label(type_),
        'product_number_sequence_available': product_number_sequence_available,
        'form': form,
    }


@blueprint.post('/for_shop/<shop_id>/<type_name>')
@permission_required('shop_product.administrate')
def create(shop_id, type_name):
    """Create a product."""
    shop = _get_shop_or_404(shop_id)
    type_ = _get_product_type_or_400(type_name)

    form = _get_create_form(type_, shop.id, request)

    product_number_sequences = _get_active_product_number_sequences_for_shop(
        shop.id
    )
    if not product_number_sequences:
        flash_error(
            gettext('No product number sequences are defined for this shop.')
        )
        return create_form(shop_id, type_.name, form)

    form.set_product_number_sequence_choices(product_number_sequences)
    if type_ in (ProductType.ticket, ProductType.ticket_bundle):
        form.set_ticket_category_choices(shop.brand_id)

    if not form.validate():
        return create_form(shop_id, type_.name, form)

    product_number_sequence_id = form.product_number_sequence_id.data
    if not product_number_sequence_id:
        flash_error(gettext('No valid product number sequence was specified.'))
        return create_form(shop_id, type_.name, form)

    product_number_sequence = (
        product_sequence_service.get_product_number_sequence(
            product_number_sequence_id
        )
    )
    if product_number_sequence.shop_id != shop.id:
        flash_error(gettext('No valid product number sequence was specified.'))
        return create_form(shop_id, type_.name, form)

    item_number = _get_item_number(product_number_sequence.id)

    name = form.name.data.strip()
    price = Money(form.price_amount.data, shop.currency)
    tax_rate = form.tax_rate.data / TAX_RATE_DISPLAY_FACTOR
    available_from_local = form.available_from.data
    available_from_utc = (
        to_utc(available_from_local) if available_from_local else None
    )
    available_until_local = form.available_until.data
    available_until_utc = (
        to_utc(available_until_local) if available_until_local else None
    )
    total_quantity = form.total_quantity.data
    max_quantity_per_order = form.max_quantity_per_order.data
    not_directly_orderable = form.not_directly_orderable.data
    separate_order_required = form.separate_order_required.data

    product = _create_product(
        type_,
        shop.id,
        item_number,
        name,
        price,
        tax_rate,
        total_quantity,
        max_quantity_per_order,
        form,
        available_from_utc,
        available_until_utc,
        not_directly_orderable,
        separate_order_required,
    )

    flash_success(
        gettext(
            'Product "%(item_number)s" has been created.',
            item_number=product.item_number,
        )
    )
    return redirect_to('.view', product_id=product.id)


def _get_create_form(type_: ProductType, shop_id: ShopID, request):
    if type_ == ProductType.ticket:
        return TicketProductCreateForm(shop_id, request.form)
    elif type_ == ProductType.ticket_bundle:
        return TicketBundleProductCreateForm(shop_id, request.form)
    else:
        return ProductCreateForm(shop_id, request.form)


def _get_item_number(product_number_sequence_id) -> ProductNumber:
    generation_result = product_sequence_service.generate_product_number(
        product_number_sequence_id
    )

    if generation_result.is_err():
        abort(500, generation_result.unwrap_err())

    return generation_result.unwrap()


def _create_product(
    type_: ProductType,
    shop_id: ShopID,
    item_number: ProductNumber,
    name: str,
    price: Money,
    tax_rate: Decimal,
    total_quantity: int,
    max_quantity_per_order: int,
    form,
    available_from: datetime | None = None,
    available_until: datetime | None = None,
    not_directly_orderable: bool = False,
    separate_order_required: bool = False,
) -> Product:
    if type_ == ProductType.ticket:
        return product_service.create_ticket_product(
            shop_id,
            item_number,
            name,
            price,
            tax_rate,
            total_quantity,
            max_quantity_per_order,
            form.ticket_category_id.data,
            available_from=available_from,
            available_until=available_until,
            not_directly_orderable=not_directly_orderable,
            separate_order_required=separate_order_required,
        )
    elif type_ == ProductType.ticket_bundle:
        return product_service.create_ticket_bundle_product(
            shop_id,
            item_number,
            name,
            price,
            tax_rate,
            total_quantity,
            max_quantity_per_order,
            form.ticket_category_id.data,
            form.ticket_quantity.data,
            available_from=available_from,
            available_until=available_until,
            not_directly_orderable=not_directly_orderable,
            separate_order_required=separate_order_required,
        )
    else:
        processing_required = type_ == ProductType.physical

        return product_service.create_product(
            shop_id,
            item_number,
            type_,
            name,
            price,
            tax_rate,
            total_quantity,
            max_quantity_per_order,
            processing_required,
            available_from=available_from,
            available_until=available_until,
            not_directly_orderable=not_directly_orderable,
            separate_order_required=separate_order_required,
        )


# -------------------------------------------------------------------- #
# update


@blueprint.get('/<uuid:product_id>/update')
@permission_required('shop_product.administrate')
@templated
def update_form(product_id, erroneous_form=None):
    """Show form to update a product."""
    product = _get_product_or_404(product_id)

    shop = shop_service.get_shop(product.shop_id)

    brand = brand_service.get_brand(shop.brand_id)

    data = dataclasses.asdict(product)
    data['price_amount'] = product.price.amount
    if product.available_from:
        data['available_from'] = to_user_timezone(product.available_from)
    if product.available_until:
        data['available_until'] = to_user_timezone(product.available_until)

    form = (
        erroneous_form
        if erroneous_form
        else ProductUpdateForm(shop.id, product.name, data=data)
    )
    form.tax_rate.data = product.tax_rate * TAX_RATE_DISPLAY_FACTOR

    return {
        'product': product,
        'shop': shop,
        'brand': brand,
        'form': form,
    }


@blueprint.post('/<uuid:product_id>')
@permission_required('shop_product.administrate')
def update(product_id):
    """Update a product."""
    product = _get_product_or_404(product_id)

    shop = shop_service.get_shop(product.shop_id)

    form = ProductUpdateForm(shop.id, product.name, request.form)
    if not form.validate():
        return update_form(product_id, form)

    name = form.name.data.strip()
    price = Money(form.price_amount.data, shop.currency)
    tax_rate = form.tax_rate.data / TAX_RATE_DISPLAY_FACTOR
    available_from_local = form.available_from.data
    available_from_utc = (
        to_utc(available_from_local) if available_from_local else None
    )
    available_until_local = form.available_until.data
    available_until_utc = (
        to_utc(available_until_local) if available_until_local else None
    )
    total_quantity = form.total_quantity.data
    max_quantity_per_order = form.max_quantity_per_order.data
    not_directly_orderable = form.not_directly_orderable.data
    separate_order_required = form.separate_order_required.data
    archived = form.archived.data

    product = product_service.update_product(
        product.id,
        name,
        price,
        tax_rate,
        available_from_utc,
        available_until_utc,
        total_quantity,
        max_quantity_per_order,
        not_directly_orderable,
        separate_order_required,
        archived,
    )

    flash_success(
        gettext('Product "%(name)s" has been updated.', name=product.name)
    )
    return redirect_to('.view', product_id=product.id)


# -------------------------------------------------------------------- #
# product attachments


@blueprint.get('/<uuid:product_id>/attachments/create')
@permission_required('shop_product.administrate')
@templated
def attachment_create_form(product_id, erroneous_form=None):
    """Show form to attach a product to another product."""
    product = _get_product_or_404(product_id)

    shop = shop_service.get_shop(product.shop_id)

    brand = brand_service.get_brand(shop.brand_id)

    attachable_products = product_service.get_attachable_products(product.id)

    form = (
        erroneous_form
        if erroneous_form
        else ProductAttachmentCreateForm(quantity=0)
    )
    form.set_product_to_attach_choices(attachable_products)

    return {
        'product': product,
        'shop': shop,
        'brand': brand,
        'form': form,
    }


@blueprint.post('/<uuid:product_id>/attachments')
@permission_required('shop_product.administrate')
def attachment_create(product_id):
    """Attach a product to another product."""
    product = _get_product_or_404(product_id)

    attachable_products = product_service.get_attachable_products(product.id)

    form = ProductAttachmentCreateForm(request.form)
    form.set_product_to_attach_choices(attachable_products)

    if not form.validate():
        return attachment_create_form(product_id, form)

    product_to_attach_id = form.product_to_attach_id.data
    product_to_attach = product_service.get_product(product_to_attach_id)
    quantity = form.quantity.data

    product_service.attach_product(product_to_attach.id, quantity, product.id)

    flash_success(
        gettext(
            'Product "%(product_to_attach_item_number)s" has been attached %(quantity)s times to product "%(product_item_number)s".',
            product_to_attach_item_number=product_to_attach.item_number,
            quantity=quantity,
            product_item_number=product.item_number,
        )
    )
    return redirect_to('.view', product_id=product.id)


@blueprint.delete('/attachments/<uuid:product_id>')
@permission_required('shop_product.administrate')
@respond_no_content
def attachment_remove(product_id):
    """Remove the attachment link from one product to another."""
    attached_product = product_service.find_attached_product(product_id)

    if attached_product is None:
        abort(404)

    product = attached_product.product
    attached_to_product = attached_product.attached_to_product

    product_service.unattach_product(attached_product.id)

    flash_success(
        gettext(
            'Product "%(product_number)s" is no longer attached to product "%(attached_to_product_number)s".',
            product_number=product.item_number,
            attached_to_product_number=attached_to_product.item_number,
        )
    )


# -------------------------------------------------------------------- #
# actions


@blueprint.get('/<uuid:product_id>/actions/badge_awarding/create')
@permission_required('shop_product.administrate')
@templated
def action_create_form_for_badge_awarding(product_id, erroneous_form=None):
    """Show form to register a badge awarding action for the product."""
    product = _get_product_or_404(product_id)

    shop = shop_service.get_shop(product.shop_id)
    brand = brand_service.get_brand(shop.brand_id)

    badges = user_badge_service.get_all_badges()

    form = (
        erroneous_form if erroneous_form else RegisterBadgeAwardingActionForm()
    )
    form.set_badge_choices(badges)

    return {
        'product': product,
        'shop': shop,
        'brand': brand,
        'form': form,
    }


@blueprint.post('/<uuid:product_id>/actions/badge_awarding')
@permission_required('shop_product.administrate')
def action_create_for_badge_awarding(product_id):
    """Register a badge awarding action for the product."""
    product = _get_product_or_404(product_id)

    badges = user_badge_service.get_all_badges()

    form = RegisterBadgeAwardingActionForm(request.form)
    form.set_badge_choices(badges)

    if not form.validate():
        return action_create_form_for_badge_awarding(product_id, form)

    badge_id = form.badge_id.data
    badge = user_badge_service.get_badge(badge_id)

    order_action_registry_service.register_badge_awarding(product.id, badge.id)

    flash_success(gettext('Action has been added.'))

    return redirect_to('.view', product_id=product.id)


@blueprint.get('/<uuid:product_id>/actions/tickets_creation/create')
@permission_required('shop_product.administrate')
@templated
def action_create_form_for_tickets_creation(product_id, erroneous_form=None):
    """Show form to register a tickets creation action for the product."""
    product = _get_product_or_404(product_id)

    shop = shop_service.get_shop(product.shop_id)
    brand = brand_service.get_brand(shop.brand_id)

    form = (
        erroneous_form
        if erroneous_form
        else RegisterTicketsCreationActionForm()
    )
    form.set_category_choices(brand.id)

    return {
        'product': product,
        'shop': shop,
        'brand': brand,
        'form': form,
    }


@blueprint.post('/<uuid:product_id>/actions/tickets_creation')
@permission_required('shop_product.administrate')
def action_create_for_tickets_creation(product_id):
    """Register a tickets creation action for the product."""
    product = _get_product_or_404(product_id)

    shop = shop_service.get_shop(product.shop_id)
    brand = brand_service.get_brand(shop.brand_id)

    form = RegisterTicketsCreationActionForm(request.form)
    form.set_category_choices(brand.id)

    if not form.validate():
        return action_create_form_for_tickets_creation(product_id, form)

    category_id = form.category_id.data
    category = ticket_category_service.get_category(category_id)

    order_action_registry_service.register_tickets_creation(
        product.id, category.id
    )

    flash_success(gettext('Action has been added.'))

    return redirect_to('.view', product_id=product.id)


@blueprint.get('/<uuid:product_id>/actions/ticket_bundles_creation/create')
@permission_required('shop_product.administrate')
@templated
def action_create_form_for_ticket_bundles_creation(
    product_id, erroneous_form=None
):
    """Show form to register a ticket bundles creation action for the product."""
    product = _get_product_or_404(product_id)

    shop = shop_service.get_shop(product.shop_id)
    brand = brand_service.get_brand(shop.brand_id)

    form = (
        erroneous_form
        if erroneous_form
        else RegisterTicketBundlesCreationActionForm()
    )
    form.set_category_choices(brand.id)

    return {
        'product': product,
        'shop': shop,
        'brand': brand,
        'form': form,
    }


@blueprint.post('/<uuid:product_id>/actions/ticket_bundles_creation')
@permission_required('shop_product.administrate')
def action_create_for_ticket_bundles_creation(product_id):
    """Register a ticket bundles creation action for the product."""
    product = _get_product_or_404(product_id)

    shop = shop_service.get_shop(product.shop_id)
    brand = brand_service.get_brand(shop.brand_id)

    form = RegisterTicketBundlesCreationActionForm(request.form)
    form.set_category_choices(brand.id)

    if not form.validate():
        return action_create_form_for_ticket_bundles_creation(product_id, form)

    category_id = form.category_id.data
    category = ticket_category_service.get_category(category_id)

    ticket_quantity = form.ticket_quantity.data

    order_action_registry_service.register_ticket_bundles_creation(
        product.id, category.id, ticket_quantity
    )

    flash_success(gettext('Action has been added.'))

    return redirect_to('.view', product_id=product.id)


@blueprint.delete('/actions/<uuid:action_id>')
@permission_required('shop_product.administrate')
@respond_no_content
def action_remove(action_id):
    """Remove the action from the product."""
    action = order_action_service.find_action(action_id)

    if action is None:
        abort(404)

    order_action_service.delete_action(action.id)

    flash_success(gettext('Action has been removed.'))


# -------------------------------------------------------------------- #
# product number sequences


@blueprint.get('/number_sequences/for_shop/<shop_id>/create')
@permission_required('shop_product.administrate')
@templated
def create_number_sequence_form(shop_id, erroneous_form=None):
    """Show form to create a product number sequence."""
    shop = _get_shop_or_404(shop_id)

    brand = brand_service.get_brand(shop.brand_id)

    form = (
        erroneous_form if erroneous_form else ProductNumberSequenceCreateForm()
    )

    return {
        'shop': shop,
        'brand': brand,
        'form': form,
    }


@blueprint.post('/number_sequences/for_shop/<shop_id>')
@permission_required('shop_product.administrate')
def create_number_sequence(shop_id):
    """Create a product number sequence."""
    shop = _get_shop_or_404(shop_id)

    form = ProductNumberSequenceCreateForm(request.form)
    if not form.validate():
        return create_number_sequence_form(shop_id, form)

    prefix = form.prefix.data.strip()

    creation_result = product_sequence_service.create_product_number_sequence(
        shop.id, prefix
    )
    if creation_result.is_err():
        flash_error(
            gettext(
                'Product number sequence could not be created. '
                'Is prefix "%(prefix)s" already defined?',
                prefix=prefix,
            )
        )
        return create_number_sequence_form(shop.id, form)

    flash_success(
        gettext(
            'Product number sequence with prefix "%(prefix)s" has been created.',
            prefix=prefix,
        )
    )
    return redirect_to('.index_for_shop', shop_id=shop.id)


# -------------------------------------------------------------------- #
# helpers


def _get_shop_or_404(shop_id):
    shop = shop_service.find_shop(shop_id)

    if shop is None:
        abort(404)

    return shop


def _get_product_or_404(product_id) -> Product:
    product = product_service.find_product(product_id)

    if product is None:
        abort(404)

    return product


def _get_product_type_or_400(value: str) -> ProductType:
    try:
        return ProductType[value]
    except KeyError:
        abort(400, f'Unknown product type "{value}"')


def _get_active_product_number_sequences_for_shop(
    shop_id: ShopID,
) -> list[ProductNumberSequence]:
    sequences = product_sequence_service.get_product_number_sequences_for_shop(
        shop_id
    )
    return [sequence for sequence in sequences if not sequence.archived]


def _assemble_datetime_utc(d: date, t: time) -> datetime | None:
    if not d or not t:
        return None

    local_dt = datetime.combine(d, t)
    return to_utc(local_dt)
