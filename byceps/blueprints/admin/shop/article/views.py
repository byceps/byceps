"""
byceps.blueprints.admin.shop.article.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import dataclasses
from datetime import datetime
from decimal import Decimal

from flask import abort, request
from flask_babel import gettext, to_user_timezone, to_utc

from .....services.brand import brand_service
from .....services.party import party_service
from .....services.shop.article import article_sequence_service, article_service
from .....services.shop.article.transfer.models import (
    Article,
    ArticleType,
    get_article_type_label,
)
from .....services.shop.order import (
    action_registry_service,
    action_service,
    ordered_articles_service,
    order_service,
)
from .....services.shop.order.transfer.order import PaymentState
from .....services.shop.shop import shop_service
from .....services.ticketing import ticket_category_service
from .....services.user import user_service
from .....services.user_badge import user_badge_service
from .....util.framework.blueprint import create_blueprint
from .....util.framework.flash import flash_error, flash_success
from .....util.framework.templating import templated
from .....util.views import permission_required, redirect_to, respond_no_content

from .forms import (
    ArticleCreateForm,
    ArticleUpdateForm,
    ArticleAttachmentCreateForm,
    ArticleNumberSequenceCreateForm,
    RegisterBadgeAwardingActionForm,
    RegisterTicketBundlesCreationActionForm,
    RegisterTicketsCreationActionForm,
    TicketArticleCreateForm,
    TicketBundleArticleCreateForm,
)


blueprint = create_blueprint('shop_article_admin', __name__)


TAX_RATE_DISPLAY_FACTOR = Decimal('100')


@blueprint.get('/for_shop/<shop_id>', defaults={'page': 1})
@blueprint.get('/for_shop/<shop_id>/pages/<int:page>')
@permission_required('shop_article.view')
@templated
def index_for_shop(shop_id, page):
    """List articles for that shop."""
    shop = _get_shop_or_404(shop_id)

    brand = brand_service.get_brand(shop.brand_id)

    per_page = request.args.get('per_page', type=int, default=15)

    search_term = request.args.get('search_term', default='').strip()

    articles = article_service.get_articles_for_shop_paginated(
        shop.id,
        page,
        per_page,
        search_term=search_term,
    )

    # Inherit order of enum members.
    article_type_labels_by_type = {
        type_: get_article_type_label(type_) for type_ in ArticleType
    }

    totals_by_article_number = {
        article.item_number: ordered_articles_service.count_ordered_articles(
            article.item_number
        )
        for article in articles.items
    }

    return {
        'shop': shop,
        'brand': brand,
        'articles': articles,
        'article_type_labels_by_type': article_type_labels_by_type,
        'totals_by_article_number': totals_by_article_number,
        'PaymentState': PaymentState,
        'per_page': per_page,
        'search_term': search_term,
    }


@blueprint.get('/<uuid:article_id>')
@permission_required('shop_article.view')
@templated
def view(article_id):
    """Show a single article."""
    article = article_service.find_article_with_details(article_id)
    if article is None:
        abort(404)

    shop = shop_service.get_shop(article.shop_id)

    brand = brand_service.get_brand(shop.brand_id)

    type_label = get_article_type_label(article.type_)

    if article.type_ in (ArticleType.ticket, ArticleType.ticket_bundle):
        ticket_category = ticket_category_service.find_category(
            article.type_params['ticket_category_id']
        )
        if ticket_category is not None:
            ticket_party = party_service.get_party(ticket_category.party_id)
        else:
            ticket_party = None
    else:
        ticket_party = None
        ticket_category = None

    totals = ordered_articles_service.count_ordered_articles(
        article.item_number
    )

    actions = action_service.get_actions_for_article(article.item_number)
    actions.sort(key=lambda a: a.payment_state.name, reverse=True)

    return {
        'article': article,
        'shop': shop,
        'brand': brand,
        'type_label': type_label,
        'ticket_category': ticket_category,
        'ticket_party': ticket_party,
        'totals': totals,
        'PaymentState': PaymentState,
        'actions': actions,
    }


@blueprint.get('/<uuid:article_id>/ordered')
@permission_required('shop_article.view')
@templated
def view_ordered(article_id):
    """List the people that have ordered this article, and the
    corresponding quantities.
    """
    article = _get_article_or_404(article_id)

    shop = shop_service.get_shop(article.shop_id)

    brand = brand_service.get_brand(shop.brand_id)

    line_items = ordered_articles_service.get_line_items_for_article(
        article.item_number
    )

    quantity_total = sum(item.quantity for item in line_items)

    order_numbers = {item.order_number for item in line_items}
    orders = order_service.get_orders_for_order_numbers(order_numbers)
    orders_by_order_numbers = {order.order_number: order for order in orders}

    user_ids = {order.placed_by_id for order in orders}
    users = user_service.get_users(user_ids, include_avatars=True)
    users_by_id = user_service.index_users_by_id(users)

    def transform(line_item):
        quantity = line_item.quantity
        order = orders_by_order_numbers[line_item.order_number]
        user = users_by_id[order.placed_by_id]

        return quantity, order, user

    quantities_orders_users = list(map(transform, line_items))

    return {
        'article': article,
        'shop': shop,
        'brand': brand,
        'quantity_total': quantity_total,
        'quantities_orders_users': quantities_orders_users,
        'now': datetime.utcnow(),
    }


# -------------------------------------------------------------------- #
# create


@blueprint.get('/for_shop/<shop_id>/create/<type>')
@permission_required('shop_article.create')
@templated
def create_form(shop_id, type, erroneous_form=None):
    """Show form to create an article."""
    shop = _get_shop_or_404(shop_id)
    type_ = _get_article_type_or_400(type)

    brand = brand_service.get_brand(shop.brand_id)

    article_number_sequences = (
        article_sequence_service.get_article_number_sequences_for_shop(shop.id)
    )
    article_number_sequence_available = bool(article_number_sequences)

    form = (
        erroneous_form
        if erroneous_form
        else ArticleCreateForm(price=Decimal('0.0'), tax_rate=Decimal('19.0'))
    )
    form.set_article_number_sequence_choices(article_number_sequences)

    return {
        'shop': shop,
        'brand': brand,
        'article_type_name': type_.name,
        'article_type_label': get_article_type_label(type_),
        'article_number_sequence_available': article_number_sequence_available,
        'form': form,
    }


@blueprint.get('/for_shop/<shop_id>/create/ticket')
@permission_required('shop_article.create')
@templated
def create_ticket_form(shop_id, erroneous_form=None):
    """Show form to create a ticket article."""
    shop = _get_shop_or_404(shop_id)
    type_ = ArticleType.ticket

    brand = brand_service.get_brand(shop.brand_id)

    article_number_sequences = (
        article_sequence_service.get_article_number_sequences_for_shop(shop.id)
    )
    article_number_sequence_available = bool(article_number_sequences)

    form = (
        erroneous_form
        if erroneous_form
        else TicketArticleCreateForm(
            price=Decimal('0.0'), tax_rate=Decimal('19.0')
        )
    )
    form.set_article_number_sequence_choices(article_number_sequences)
    form.set_ticket_category_choices(brand.id)

    return {
        'shop': shop,
        'brand': brand,
        'article_type_name': type_.name,
        'article_type_label': get_article_type_label(type_),
        'article_number_sequence_available': article_number_sequence_available,
        'form': form,
    }


@blueprint.get('/for_shop/<shop_id>/create/ticket_bundle')
@permission_required('shop_article.create')
@templated
def create_ticket_bundle_form(shop_id, erroneous_form=None):
    """Show form to create a ticket bundle article."""
    shop = _get_shop_or_404(shop_id)
    type_ = ArticleType.ticket_bundle

    brand = brand_service.get_brand(shop.brand_id)

    article_number_sequences = (
        article_sequence_service.get_article_number_sequences_for_shop(shop.id)
    )
    article_number_sequence_available = bool(article_number_sequences)

    form = (
        erroneous_form
        if erroneous_form
        else TicketBundleArticleCreateForm(
            price=Decimal('0.0'), tax_rate=Decimal('19.0')
        )
    )
    form.set_article_number_sequence_choices(article_number_sequences)
    form.set_ticket_category_choices(brand.id)

    return {
        'shop': shop,
        'brand': brand,
        'article_type_name': type_.name,
        'article_type_label': get_article_type_label(type_),
        'article_number_sequence_available': article_number_sequence_available,
        'form': form,
    }


@blueprint.post('/for_shop/<shop_id>/<type>')
@permission_required('shop_article.create')
def create(shop_id, type):
    """Create an article."""
    shop = _get_shop_or_404(shop_id)
    type_ = _get_article_type_or_400(type)

    if type_ == ArticleType.ticket:
        form = TicketArticleCreateForm(request.form)
    elif type_ == ArticleType.ticket_bundle:
        form = TicketBundleArticleCreateForm(request.form)
    else:
        form = ArticleCreateForm(request.form)

    article_number_sequences = (
        article_sequence_service.get_article_number_sequences_for_shop(shop.id)
    )
    if not article_number_sequences:
        flash_error(
            gettext('No article number sequences are defined for this shop.')
        )
        return create_form(shop_id, type_, form)

    form.set_article_number_sequence_choices(article_number_sequences)
    if type_ in (ArticleType.ticket, ArticleType.ticket_bundle):
        form.set_ticket_category_choices(shop.brand_id)

    if not form.validate():
        return create_form(shop_id, type_, form)

    article_number_sequence_id = form.article_number_sequence_id.data
    if not article_number_sequence_id:
        flash_error(gettext('No valid article number sequence was specified.'))
        return create_form(shop_id, type_, form)

    article_number_sequence = (
        article_sequence_service.get_article_number_sequence(
            article_number_sequence_id
        )
    )
    if article_number_sequence.shop_id != shop.id:
        flash_error(gettext('No valid article number sequence was specified.'))
        return create_form(shop_id, type_, form)

    try:
        item_number = article_sequence_service.generate_article_number(
            article_number_sequence.id
        )
    except article_sequence_service.ArticleNumberGenerationFailed as e:
        abort(500, e.message)

    description = form.description.data.strip()
    price = form.price.data
    tax_rate = form.tax_rate.data / TAX_RATE_DISPLAY_FACTOR
    total_quantity = form.total_quantity.data
    quantity = total_quantity
    max_quantity_per_order = form.max_quantity_per_order.data

    if type_ == ArticleType.ticket:
        article = article_service.create_ticket_article(
            shop.id,
            item_number,
            description,
            price,
            tax_rate,
            total_quantity,
            max_quantity_per_order,
            form.ticket_category_id.data,
        )
    elif type_ == ArticleType.ticket_bundle:
        article = article_service.create_ticket_bundle_article(
            shop.id,
            item_number,
            description,
            price,
            tax_rate,
            total_quantity,
            max_quantity_per_order,
            form.ticket_category_id.data,
            form.ticket_quantity.data,
        )
    else:
        processing_required = type_ == ArticleType.physical

        article = article_service.create_article(
            shop.id,
            item_number,
            type_,
            description,
            price,
            tax_rate,
            total_quantity,
            max_quantity_per_order,
            processing_required,
        )

    flash_success(
        gettext(
            'Article "%(item_number)s" has been created.',
            item_number=article.item_number,
        )
    )
    return redirect_to('.view', article_id=article.id)


# -------------------------------------------------------------------- #
# update


@blueprint.get('/<uuid:article_id>/update')
@permission_required('shop_article.update')
@templated
def update_form(article_id, erroneous_form=None):
    """Show form to update an article."""
    article = _get_article_or_404(article_id)

    shop = shop_service.get_shop(article.shop_id)

    brand = brand_service.get_brand(shop.brand_id)

    data = dataclasses.asdict(article)
    if article.available_from:
        available_from_local = to_user_timezone(article.available_from)
        data['available_from_date'] = available_from_local.date()
        data['available_from_time'] = available_from_local.time()
    if article.available_until:
        available_until_local = to_user_timezone(article.available_until)
        data['available_until_date'] = available_until_local.date()
        data['available_until_time'] = available_until_local.time()

    form = erroneous_form if erroneous_form else ArticleUpdateForm(data=data)
    form.tax_rate.data = article.tax_rate * TAX_RATE_DISPLAY_FACTOR

    return {
        'article': article,
        'shop': shop,
        'brand': brand,
        'form': form,
    }


@blueprint.post('/<uuid:article_id>')
@permission_required('shop_article.update')
def update(article_id):
    """Update an article."""
    article = _get_article_or_404(article_id)

    form = ArticleUpdateForm(request.form)
    if not form.validate():
        return update_form(article_id, form)

    description = form.description.data.strip()
    price = form.price.data
    tax_rate = form.tax_rate.data / TAX_RATE_DISPLAY_FACTOR

    if form.available_from_date.data and form.available_from_time.data:
        available_from_local = datetime.combine(
            form.available_from_date.data, form.available_from_time.data
        )
        available_from_utc = to_utc(available_from_local)
    else:
        available_from_utc = None

    if form.available_until_date.data and form.available_until_time.data:
        available_until_local = datetime.combine(
            form.available_until_date.data, form.available_until_time.data
        )
        available_until_utc = to_utc(available_until_local)
    else:
        available_until_utc = None

    total_quantity = form.total_quantity.data
    max_quantity_per_order = form.max_quantity_per_order.data
    not_directly_orderable = form.not_directly_orderable.data
    separate_order_required = form.separate_order_required.data

    article = article_service.update_article(
        article.id,
        description,
        price,
        tax_rate,
        available_from_utc,
        available_until_utc,
        total_quantity,
        max_quantity_per_order,
        not_directly_orderable,
        separate_order_required,
    )

    flash_success(
        gettext(
            'Article "%(description)s" has been updated.',
            description=article.description,
        )
    )
    return redirect_to('.view', article_id=article.id)


# -------------------------------------------------------------------- #
# article attachments


@blueprint.get('/<uuid:article_id>/attachments/create')
@permission_required('shop_article.update')
@templated
def attachment_create_form(article_id, erroneous_form=None):
    """Show form to attach an article to another article."""
    article = _get_article_or_404(article_id)

    shop = shop_service.get_shop(article.shop_id)

    brand = brand_service.get_brand(shop.brand_id)

    attachable_articles = article_service.get_attachable_articles(article.id)

    form = (
        erroneous_form
        if erroneous_form
        else ArticleAttachmentCreateForm(quantity=0)
    )
    form.set_article_to_attach_choices(attachable_articles)

    return {
        'article': article,
        'shop': shop,
        'brand': brand,
        'form': form,
    }


@blueprint.post('/<uuid:article_id>/attachments')
@permission_required('shop_article.update')
def attachment_create(article_id):
    """Attach an article to another article."""
    article = _get_article_or_404(article_id)

    attachable_articles = article_service.get_attachable_articles(article.id)

    form = ArticleAttachmentCreateForm(request.form)
    form.set_article_to_attach_choices(attachable_articles)

    if not form.validate():
        return attachment_create_form(article_id, form)

    article_to_attach_id = form.article_to_attach_id.data
    article_to_attach = article_service.get_article(article_to_attach_id)
    quantity = form.quantity.data

    article_service.attach_article(
        article_to_attach.item_number, quantity, article.item_number
    )

    flash_success(
        gettext(
            'Article "%(article_to_attach_item_number)s" has been attached %(quantity)s times to article "%(article_item_number)s".',
            article_to_attach_item_number=article_to_attach.item_number,
            quantity=quantity,
            article_item_number=article.item_number,
        )
    )
    return redirect_to('.view', article_id=article.id)


@blueprint.delete('/attachments/<uuid:article_id>')
@permission_required('shop_article.update')
@respond_no_content
def attachment_remove(article_id):
    """Remove the attachment link from one article to another."""
    attached_article = article_service.find_attached_article(article_id)

    if attached_article is None:
        abort(404)

    article = attached_article.article
    attached_to_article = attached_article.attached_to_article

    article_service.unattach_article(attached_article.id)

    flash_success(
        gettext(
            'Article "%(article_item_number)s" is no longer attached to article "%(attached_to_article_item_number)s".',
            article_item_number=article.item_number,
            attached_to_article_item_number=attached_to_article.item_number,
        )
    )


# -------------------------------------------------------------------- #
# actions


@blueprint.get('/<uuid:article_id>/actions/badge_awarding/create')
@permission_required('shop_article.update')
@templated
def action_create_form_for_badge_awarding(article_id, erroneous_form=None):
    """Show form to register a badge awarding action for the article."""
    article = _get_article_or_404(article_id)

    shop = shop_service.get_shop(article.shop_id)
    brand = brand_service.get_brand(shop.brand_id)

    badges = user_badge_service.get_all_badges()

    form = (
        erroneous_form if erroneous_form else RegisterBadgeAwardingActionForm()
    )
    form.set_badge_choices(badges)

    return {
        'article': article,
        'shop': shop,
        'brand': brand,
        'form': form,
    }


@blueprint.post('/<uuid:article_id>/actions/badge_awarding')
@permission_required('shop_article.update')
def action_create_for_badge_awarding(article_id):
    """Register a badge awarding action for the article."""
    article = _get_article_or_404(article_id)

    badges = user_badge_service.get_all_badges()

    form = RegisterBadgeAwardingActionForm(request.form)
    form.set_badge_choices(badges)

    if not form.validate():
        return action_create_form_for_badge_awarding(article_id, form)

    badge_id = form.badge_id.data
    badge = user_badge_service.get_badge(badge_id)

    action_registry_service.register_badge_awarding(
        article.item_number, badge.id
    )

    flash_success(gettext('Action has been added.'))

    return redirect_to('.view', article_id=article.id)


@blueprint.get('/<uuid:article_id>/actions/tickets_creation/create')
@permission_required('shop_article.update')
@templated
def action_create_form_for_tickets_creation(article_id, erroneous_form=None):
    """Show form to register a tickets creation action for the article."""
    article = _get_article_or_404(article_id)

    shop = shop_service.get_shop(article.shop_id)
    brand = brand_service.get_brand(shop.brand_id)

    form = (
        erroneous_form
        if erroneous_form
        else RegisterTicketsCreationActionForm()
    )
    form.set_category_choices(brand.id)

    return {
        'article': article,
        'shop': shop,
        'brand': brand,
        'form': form,
    }


@blueprint.post('/<uuid:article_id>/actions/tickets_creation')
@permission_required('shop_article.update')
def action_create_for_tickets_creation(article_id):
    """Register a tickets creation action for the article."""
    article = _get_article_or_404(article_id)

    shop = shop_service.get_shop(article.shop_id)
    brand = brand_service.get_brand(shop.brand_id)

    form = RegisterTicketsCreationActionForm(request.form)
    form.set_category_choices(brand.id)

    if not form.validate():
        return action_create_form_for_tickets_creation(article_id, form)

    category_id = form.category_id.data
    category = ticket_category_service.get_category(category_id)

    action_registry_service.register_tickets_creation(
        article.item_number, category.id
    )

    flash_success(gettext('Action has been added.'))

    return redirect_to('.view', article_id=article.id)


@blueprint.get('/<uuid:article_id>/actions/ticket_bundles_creation/create')
@permission_required('shop_article.update')
@templated
def action_create_form_for_ticket_bundles_creation(
    article_id, erroneous_form=None
):
    """Show form to register a ticket bundles creation action for the article."""
    article = _get_article_or_404(article_id)

    shop = shop_service.get_shop(article.shop_id)
    brand = brand_service.get_brand(shop.brand_id)

    form = (
        erroneous_form
        if erroneous_form
        else RegisterTicketBundlesCreationActionForm()
    )
    form.set_category_choices(brand.id)

    return {
        'article': article,
        'shop': shop,
        'brand': brand,
        'form': form,
    }


@blueprint.post('/<uuid:article_id>/actions/ticket_bundles_creation')
@permission_required('shop_article.update')
def action_create_for_ticket_bundles_creation(article_id):
    """Register a ticket bundles creation action for the article."""
    article = _get_article_or_404(article_id)

    shop = shop_service.get_shop(article.shop_id)
    brand = brand_service.get_brand(shop.brand_id)

    form = RegisterTicketBundlesCreationActionForm(request.form)
    form.set_category_choices(brand.id)

    if not form.validate():
        return action_create_form_for_ticket_bundles_creation(article_id, form)

    category_id = form.category_id.data
    category = ticket_category_service.get_category(category_id)

    ticket_quantity = form.ticket_quantity.data

    action_registry_service.register_ticket_bundles_creation(
        article.item_number, category.id, ticket_quantity
    )

    flash_success(gettext('Action has been added.'))

    return redirect_to('.view', article_id=article.id)


@blueprint.delete('/actions/<uuid:action_id>')
@permission_required('shop_article.update')
@respond_no_content
def action_remove(action_id):
    """Remove the action from the article."""
    action = action_service.find_action(action_id)

    if action is None:
        abort(404)

    action_service.delete_action(action.id)

    flash_success(gettext('Action has been removed.'))


# -------------------------------------------------------------------- #
# article number sequences


@blueprint.get('/number_sequences/for_shop/<shop_id>/create')
@permission_required('shop_article.create')
@templated
def create_number_sequence_form(shop_id, erroneous_form=None):
    """Show form to create an article number sequence."""
    shop = _get_shop_or_404(shop_id)

    brand = brand_service.get_brand(shop.brand_id)

    form = (
        erroneous_form if erroneous_form else ArticleNumberSequenceCreateForm()
    )

    return {
        'shop': shop,
        'brand': brand,
        'form': form,
    }


@blueprint.post('/number_sequences/for_shop/<shop_id>')
@permission_required('shop_article.create')
def create_number_sequence(shop_id):
    """Create an article number sequence."""
    shop = _get_shop_or_404(shop_id)

    form = ArticleNumberSequenceCreateForm(request.form)
    if not form.validate():
        return create_number_sequence_form(shop_id, form)

    prefix = form.prefix.data.strip()

    try:
        article_sequence_service.create_article_number_sequence(shop.id, prefix)
    except article_sequence_service.ArticleNumberSequenceCreationFailed:
        flash_error(
            gettext(
                'Article number sequence could not be created. '
                'Is prefix "%(prefix)s" already defined?',
                prefix=prefix,
            )
        )
        return create_number_sequence_form(shop.id, form)

    flash_success(
        gettext(
            'Article number sequence with prefix "%(prefix)s" has been created.',
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


def _get_article_or_404(article_id) -> Article:
    article = article_service.find_article(article_id)

    if article is None:
        abort(404)

    return article


def _get_article_type_or_400(value: str) -> ArticleType:
    try:
        return ArticleType[value]
    except KeyError:
        abort(400, 'Unknown article type')
