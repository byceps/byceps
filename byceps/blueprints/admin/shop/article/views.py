"""
byceps.blueprints.admin.shop.article.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from decimal import Decimal

from flask import abort, request

from .....services.shop.article import service as article_service
from .....services.shop.order import (
    ordered_articles_service,
    service as order_service,
)
from .....services.shop.order.transfer.models import PaymentState
from .....services.shop.sequence import service as sequence_service
from .....services.shop.shop import service as shop_service
from .....services.user import service as user_service
from .....util.framework.blueprint import create_blueprint
from .....util.framework.flash import flash_error, flash_success
from .....util.framework.templating import templated
from .....util.templatefilters import local_tz_to_utc, utc_to_local_tz
from .....util.views import redirect_to, respond_no_content

from ....authorization.decorators import permission_required
from ....authorization.registry import permission_registry

from .authorization import ShopArticlePermission
from .forms import (
    ArticleCreateForm,
    ArticleUpdateForm,
    ArticleAttachmentCreateForm,
)


blueprint = create_blueprint('shop_article_admin', __name__)


permission_registry.register_enum(ShopArticlePermission)


@blueprint.route('/for_shop/<shop_id>', defaults={'page': 1})
@blueprint.route('/for_shop/<shop_id>/pages/<int:page>')
@permission_required(ShopArticlePermission.view)
@templated
def index_for_shop(shop_id, page):
    """List articles for that shop."""
    shop = _get_shop_or_404(shop_id)

    per_page = request.args.get('per_page', type=int, default=15)
    articles = article_service.get_articles_for_shop_paginated(
        shop.id, page, per_page
    )

    return {
        'shop': shop,
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

    totals = ordered_articles_service.count_ordered_articles(
        article.item_number
    )

    return {
        'article': article,
        'shop': shop,
        'totals': totals,
        'PaymentState': PaymentState,
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
        'quantity_total': quantity_total,
        'quantities_orders_users': quantities_orders_users,
        'now': datetime.utcnow(),
    }


@blueprint.route('/for_shop/<shop_id>/create')
@permission_required(ShopArticlePermission.create)
@templated
def create_form(shop_id, erroneous_form=None):
    """Show form to create an article."""
    shop = _get_shop_or_404(shop_id)

    article_number_sequences = sequence_service.find_article_number_sequences_for_shop(
        shop.id
    )
    article_number_sequence_available = bool(article_number_sequences)

    form = erroneous_form if erroneous_form else ArticleCreateForm(
        price=Decimal('0.00'),
        tax_rate=Decimal('0.19'),
        quantity=0)
    form.set_article_number_sequence_choices(article_number_sequences)

    return {
        'shop': shop,
        'article_number_sequence_available': article_number_sequence_available,
        'form': form,
    }


@blueprint.route('/for_shop/<shop_id>', methods=['POST'])
@permission_required(ShopArticlePermission.create)
def create(shop_id):
    """Create an article."""
    shop = _get_shop_or_404(shop_id)

    form = ArticleCreateForm(request.form)

    article_number_sequences = sequence_service.find_article_number_sequences_for_shop(
        shop.id
    )
    if not article_number_sequences:
        flash_error(
            f'Für diesen Shop sind keine Artikelnummer-Sequenzen definiert.'
        )
        return create_form(shop_id, form)

    form.set_article_number_sequence_choices(article_number_sequences)
    if not form.validate():
        return create_form(shop_id, form)

    article_number_sequence_id = form.article_number_sequence_id.data
    if not article_number_sequence_id:
        flash_error(f'Es wurde keine gültige Artikelnummer-Sequenz angegeben.')
        return create_form(shop_id, form)

    article_number_sequence = sequence_service.find_article_number_sequence(
        article_number_sequence_id
    )
    if (article_number_sequence is None) or (
        article_number_sequence.shop_id != shop.id
    ):
        flash_error(f'Es wurde keine gültige Artikelnummer-Sequenz angegeben.')
        return create_form(shop_id, form)

    try:
        item_number = sequence_service.generate_article_number(
            article_number_sequence.id
        )
    except sequence_service.NumberGenerationFailed as e:
        abort(500, e.message)

    description = form.description.data.strip()
    price = form.price.data
    tax_rate = form.tax_rate.data
    quantity = form.quantity.data

    article = article_service.create_article(
        shop.id, item_number, description, price, tax_rate, quantity
    )

    flash_success(f'Der Artikel "{article.item_number}" wurde angelegt.')
    return redirect_to('.view', article_id=article.id)


@blueprint.route('/<uuid:article_id>/update')
@permission_required(ShopArticlePermission.update)
@templated
def update_form(article_id, erroneous_form=None):
    """Show form to update an article."""
    article = _get_article_or_404(article_id)

    shop = shop_service.get_shop(article.shop_id)

    if article.available_from:
        article.available_from = utc_to_local_tz(article.available_from)
    if article.available_until:
        article.available_until = utc_to_local_tz(article.available_until)

    form = erroneous_form if erroneous_form else ArticleUpdateForm(obj=article)

    return {
        'article': article,
        'shop': shop,
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
    tax_rate = form.tax_rate.data
    available_from = form.available_from.data
    available_until = form.available_until.data
    quantity = form.quantity.data
    max_quantity_per_order = form.max_quantity_per_order.data
    not_directly_orderable = form.not_directly_orderable.data
    requires_separate_order = form.requires_separate_order.data
    shipping_required = form.shipping_required.data

    if available_from:
        available_from = local_tz_to_utc(available_from)
    if available_until:
        available_until = local_tz_to_utc(available_until)

    article_service.update_article(
        article.id,
        description,
        price,
        tax_rate,
        available_from,
        available_until,
        quantity,
        max_quantity_per_order,
        not_directly_orderable,
        requires_separate_order,
        shipping_required,
    )

    flash_success(f'Der Artikel "{article.description}" wurde aktualisiert.')
    return redirect_to('.view', article_id=article.id)


@blueprint.route('/<uuid:article_id>/attachments/create')
@permission_required(ShopArticlePermission.update)
@templated
def attachment_create_form(article_id, erroneous_form=None):
    """Show form to attach an article to another article."""
    article = _get_article_or_404(article_id)

    shop = shop_service.get_shop(article.shop_id)

    attachable_articles = article_service.get_attachable_articles(article.id)

    form = erroneous_form if erroneous_form else ArticleAttachmentCreateForm(
        quantity=0)
    form.set_article_to_attach_choices(attachable_articles)

    return {
        'article': article,
        'shop': shop,
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
        f'Der Artikel "{article_to_attach.item_number}" '
        f'wurde {quantity:d} mal an den Artikel "{article.item_number}" '
        'angehängt.'
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
        f'Artikel "{article.item_number}" ist nun nicht mehr '
        f'an Artikel "{attached_to_article.item_number}" angehängt.'
    )


def _get_shop_or_404(shop_id):
    shop = shop_service.find_shop(shop_id)

    if shop is None:
        abort(404)

    return shop


def _get_article_or_404(article_id):
    article = article_service.find_article(article_id)

    if article is None:
        abort(404)

    return article
