"""
byceps.blueprints.admin.shop.article.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from decimal import Decimal

from flask import abort, request
from flask_babel import gettext

from .....services.brand import service as brand_service
from .....services.shop.article import (
    sequence_service as article_sequence_service,
    service as article_service,
)
from .....services.shop.order import (
    action_service as order_action_service,
    ordered_articles_service,
    service as order_service,
)
from .....services.shop.order.transfer.models import PaymentState
from .....services.shop.shop import service as shop_service
from .....services.user import service as user_service
from .....util.authorization import register_permission_enum
from .....util.framework.blueprint import create_blueprint
from .....util.framework.flash import flash_error, flash_success
from .....util.framework.templating import templated
from .....util.templatefilters import local_tz_to_utc, utc_to_local_tz
from .....util.views import permission_required, redirect_to, respond_no_content

from .authorization import ShopArticlePermission
from .forms import (
    ArticleCreateForm,
    ArticleUpdateForm,
    ArticleAttachmentCreateForm,
    ArticleNumberSequenceCreateForm,
)


blueprint = create_blueprint('shop_article_admin', __name__)


register_permission_enum(ShopArticlePermission)


TAX_RATE_DISPLAY_FACTOR = Decimal('100')


@blueprint.route('/for_shop/<shop_id>', defaults={'page': 1})
@blueprint.route('/for_shop/<shop_id>/pages/<int:page>')
@permission_required(ShopArticlePermission.view)
@templated
def index_for_shop(shop_id, page):
    """List articles for that shop."""
    shop = _get_shop_or_404(shop_id)

    brand = brand_service.get_brand(shop.brand_id)

    per_page = request.args.get('per_page', type=int, default=15)
    articles = article_service.get_articles_for_shop_paginated(
        shop.id, page, per_page
    )

    return {
        'shop': shop,
        'brand': brand,
        'articles': articles,
    }


@blueprint.route('/<uuid:article_id>')
@permission_required(ShopArticlePermission.view)
@templated
def view(article_id):
    """Show a single article."""
    article = article_service.find_article_with_details(article_id)
    if article is None:
        abort(404)

    shop = shop_service.get_shop(article.shop_id)

    brand = brand_service.get_brand(shop.brand_id)

    totals = ordered_articles_service.count_ordered_articles(
        article.item_number
    )

    actions = order_action_service.get_actions_for_article(article.item_number)
    actions.sort(key=lambda a: a.payment_state.name, reverse=True)

    return {
        'article': article,
        'shop': shop,
        'brand': brand,
        'totals': totals,
        'PaymentState': PaymentState,
        'actions': actions,
    }


@blueprint.route('/<uuid:article_id>/ordered')
@permission_required(ShopArticlePermission.view)
@templated
def view_ordered(article_id):
    """List the people that have ordered this article, and the
    corresponding quantities.
    """
    article = _get_article_or_404(article_id)

    shop = shop_service.get_shop(article.shop_id)

    brand = brand_service.get_brand(shop.brand_id)

    order_items = ordered_articles_service.get_order_items_for_article(
        article.item_number
    )

    quantity_total = sum(item.quantity for item in order_items)

    order_numbers = {item.order_number for item in order_items}
    orders = order_service.find_orders_by_order_numbers(order_numbers)
    orders_by_order_numbers = {order.order_number: order for order in orders}

    user_ids = {order.placed_by_id for order in orders}
    users = user_service.find_users(user_ids, include_avatars=True)
    users_by_id = {user.id: user for user in users}

    def transform(order_item):
        quantity = order_item.quantity
        order = orders_by_order_numbers[order_item.order_number]
        user = users_by_id[order.placed_by_id]

        return quantity, order, user

    quantities_orders_users = list(map(transform, order_items))

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


@blueprint.route('/for_shop/<shop_id>/create')
@permission_required(ShopArticlePermission.create)
@templated
def create_form(shop_id, erroneous_form=None):
    """Show form to create an article."""
    shop = _get_shop_or_404(shop_id)

    brand = brand_service.get_brand(shop.brand_id)

    article_number_sequences = (
        article_sequence_service.find_article_number_sequences_for_shop(shop.id)
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
        'article_number_sequence_available': article_number_sequence_available,
        'form': form,
    }


@blueprint.route('/for_shop/<shop_id>', methods=['POST'])
@permission_required(ShopArticlePermission.create)
def create(shop_id):
    """Create an article."""
    shop = _get_shop_or_404(shop_id)

    form = ArticleCreateForm(request.form)

    article_number_sequences = (
        article_sequence_service.find_article_number_sequences_for_shop(shop.id)
    )
    if not article_number_sequences:
        flash_error(
            gettext('No article number sequences are defined for this shop.')
        )
        return create_form(shop_id, form)

    form.set_article_number_sequence_choices(article_number_sequences)
    if not form.validate():
        return create_form(shop_id, form)

    article_number_sequence_id = form.article_number_sequence_id.data
    if not article_number_sequence_id:
        flash_error(gettext('No valid article number sequence was specified.'))
        return create_form(shop_id, form)

    article_number_sequence = (
        article_sequence_service.find_article_number_sequence(
            article_number_sequence_id
        )
    )
    if (article_number_sequence is None) or (
        article_number_sequence.shop_id != shop.id
    ):
        flash_error(gettext('No valid article number sequence was specified.'))
        return create_form(shop_id, form)

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

    article = article_service.create_article(
        shop.id,
        item_number,
        description,
        price,
        tax_rate,
        total_quantity,
        max_quantity_per_order,
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


@blueprint.route('/<uuid:article_id>/update')
@permission_required(ShopArticlePermission.update)
@templated
def update_form(article_id, erroneous_form=None):
    """Show form to update an article."""
    article = _get_article_or_404(article_id)

    shop = shop_service.get_shop(article.shop_id)

    brand = brand_service.get_brand(shop.brand_id)

    if article.available_from:
        article.available_from = utc_to_local_tz(article.available_from)
    if article.available_until:
        article.available_until = utc_to_local_tz(article.available_until)

    form = (
        erroneous_form
        if erroneous_form
        else ArticleUpdateForm(
            obj=article,
            available_from_date=article.available_from.date()
            if article.available_from
            else None,
            available_from_time=article.available_from.time()
            if article.available_from
            else None,
            available_until_date=article.available_until.date()
            if article.available_until
            else None,
            available_until_time=article.available_until.time()
            if article.available_until
            else None,
        )
    )
    form.tax_rate.data = article.tax_rate * TAX_RATE_DISPLAY_FACTOR

    return {
        'article': article,
        'shop': shop,
        'brand': brand,
        'form': form,
    }


@blueprint.route('/<uuid:article_id>', methods=['POST'])
@permission_required(ShopArticlePermission.update)
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
        available_from = local_tz_to_utc(
            datetime.combine(
                form.available_from_date.data, form.available_from_time.data
            )
        )
    else:
        available_from = None
    if form.available_until_date.data and form.available_until_time.data:
        available_until = local_tz_to_utc(
            datetime.combine(
                form.available_until_date.data, form.available_until_time.data
            )
        )
    else:
        available_until = None
    total_quantity = form.total_quantity.data
    max_quantity_per_order = form.max_quantity_per_order.data
    not_directly_orderable = form.not_directly_orderable.data
    requires_separate_order = form.requires_separate_order.data
    shipping_required = form.shipping_required.data

    article = article_service.update_article(
        article.id,
        description,
        price,
        tax_rate,
        available_from,
        available_until,
        total_quantity,
        max_quantity_per_order,
        not_directly_orderable,
        requires_separate_order,
        shipping_required,
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


@blueprint.route('/<uuid:article_id>/attachments/create')
@permission_required(ShopArticlePermission.update)
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


@blueprint.route('/<uuid:article_id>/attachments', methods=['POST'])
@permission_required(ShopArticlePermission.update)
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


@blueprint.route('/attachments/<uuid:article_id>', methods=['DELETE'])
@permission_required(ShopArticlePermission.update)
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
# article number sequences


@blueprint.route('/number_sequences/for_shop/<shop_id>/create')
@permission_required(ShopArticlePermission.create)
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


@blueprint.route('/number_sequences/for_shop/<shop_id>', methods=['POST'])
@permission_required(ShopArticlePermission.create)
def create_number_sequence(shop_id):
    """Create an article number sequence."""
    shop = _get_shop_or_404(shop_id)

    form = ArticleNumberSequenceCreateForm(request.form)
    if not form.validate():
        return create_number_sequence_form(shop_id, form)

    prefix = form.prefix.data.strip()

    sequence_id = article_sequence_service.create_article_number_sequence(
        shop.id, prefix
    )
    if sequence_id is None:
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


def _get_article_or_404(article_id):
    article = article_service.find_db_article(article_id)

    if article is None:
        abort(404)

    return article
