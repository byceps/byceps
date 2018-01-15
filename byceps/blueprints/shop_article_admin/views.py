"""
byceps.blueprints.shop_article_admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from decimal import Decimal

from flask import abort, request

from ...services.party import service as party_service
from ...services.shop.article import service as article_service
from ...services.shop.order.models.payment import PaymentState
from ...services.shop.order import ordered_articles_service
from ...services.shop.sequence import service as sequence_service
from ...services.ticketing import ticket_service
from ...util.framework.blueprint import create_blueprint
from ...util.framework.flash import flash_success
from ...util.framework.templating import templated
from ...util.views import redirect_to, respond_no_content

from ..authorization.decorators import permission_required
from ..authorization.registry import permission_registry

from .authorization import ShopArticlePermission
from .forms import ArticleCreateForm, ArticleUpdateForm, \
    ArticleAttachmentCreateForm


blueprint = create_blueprint('shop_article_admin', __name__)


permission_registry.register_enum(ShopArticlePermission)


@blueprint.route('/parties/<party_id>', defaults={'page': 1})
@blueprint.route('/parties/<party_id>/pages/<int:page>')
@permission_required(ShopArticlePermission.list)
@templated
def index_for_party(party_id, page):
    """List articles for that party."""
    party = _get_party_or_404(party_id)

    article_number_prefix = sequence_service.get_article_number_prefix(party.id)

    per_page = request.args.get('per_page', type=int, default=15)
    articles = article_service.get_articles_for_party_paginated(party.id, page,
                                                                per_page)

    return {
        'party': party,
        'article_number_prefix': article_number_prefix,
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

    totals = ordered_articles_service.count_ordered_articles(article)

    return {
        'article': article,
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

    order_items = ordered_articles_service.get_order_items_for_article(article)

    quantity_total = sum(item.quantity for item in order_items)

    def transform(order_item):
        user = order_item.order.placed_by
        tickets = ticket_service.find_tickets_used_by_user(
            user.id, article.party.id)
        quantity = order_item.quantity
        order = order_item.order
        return user, tickets, quantity, order

    users_tickets_quantities_orders = map(transform, order_items)

    return {
        'article': article,
        'quantity_total': quantity_total,
        'users_tickets_quantities_orders': users_tickets_quantities_orders,
        'now': datetime.now(),
    }


@blueprint.route('/for_party/<party_id>/create')
@permission_required(ShopArticlePermission.create)
@templated
def create_form(party_id, erroneous_form=None):
    """Show form to create an article."""
    party = _get_party_or_404(party_id)

    article_number_prefix = sequence_service.get_article_number_prefix(party.id)

    form = erroneous_form if erroneous_form else ArticleCreateForm(
        price=Decimal('0.00'),
        tax_rate=Decimal('0.19'),
        quantity=0)

    return {
        'party': party,
        'article_number_prefix': article_number_prefix,
        'form': form,
    }


@blueprint.route('/for_party/<party_id>', methods=['POST'])
@permission_required(ShopArticlePermission.create)
def create(party_id):
    """Create an article."""
    party = _get_party_or_404(party_id)

    form = ArticleCreateForm(request.form)
    if not form.validate():
        return create_form(party_id, form)

    try:
        item_number = sequence_service.generate_article_number(party.id)
    except sequence_service.NumberGenerationFailed as e:
        abort(500, e.message)

    description = form.description.data.strip()
    price = form.price.data
    tax_rate = form.tax_rate.data
    quantity = form.quantity.data

    article = article_service.create_article(party.id, item_number, description,
                                             price, tax_rate, quantity)

    flash_success('Der Artikel "{}" wurde angelegt.', article.item_number)
    return redirect_to('.view', article_id=article.id)


@blueprint.route('/<uuid:article_id>/update')
@permission_required(ShopArticlePermission.update)
@templated
def update_form(article_id, erroneous_form=None):
    """Show form to update an article."""
    article = _get_article_or_404(article_id)

    form = erroneous_form if erroneous_form else ArticleUpdateForm(obj=article)

    return {
        'form': form,
        'article': article,
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

    article_service.update_article(article, description, price, tax_rate,
                                   available_from, available_until, quantity,
                                   max_quantity_per_order,
                                   not_directly_orderable,
                                   requires_separate_order, shipping_required)

    flash_success('Der Artikel "{}" wurde aktualisiert.', article.description)
    return redirect_to('.view', article_id=article.id)


@blueprint.route('/<article_id>/attachments/create')
@permission_required(ShopArticlePermission.update)
@templated
def attachment_create_form(article_id, erroneous_form=None):
    """Show form to attach an article to another article."""
    article = _get_article_or_404(article_id)

    attachable_articles = article_service.get_attachable_articles(article)

    form = erroneous_form if erroneous_form else ArticleAttachmentCreateForm(
        quantity=0)
    form.set_article_to_attach_choices(attachable_articles)

    return {
        'article': article,
        'form': form,
    }


@blueprint.route('/<article_id>/attachments', methods=['POST'])
@permission_required(ShopArticlePermission.update)
def attachment_create(article_id):
    """Attach an article to another article."""
    article = _get_article_or_404(article_id)

    attachable_articles = article_service.get_attachable_articles(article)

    form = ArticleAttachmentCreateForm(request.form)
    form.set_article_to_attach_choices(attachable_articles)

    if not form.validate():
        return attachment_create_form(article_id, form)

    article_to_attach_id = form.article_to_attach_id.data
    article_to_attach = article_service.find_article(article_to_attach_id)
    quantity = form.quantity.data

    article_service.attach_article(article_to_attach, quantity, article)

    flash_success(
        'Der Artikel "{}" wurde {:d} mal an den Artikel "{}" angehängt.',
        article_to_attach.item_number, quantity, article.item_number)
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

    article_service.unattach_article(attached_article)

    flash_success('Artikel "{}" ist nun nicht mehr an Artikel "{}" angehängt.',
                  article.item_number, attached_to_article.item_number)


def _get_party_or_404(party_id):
    party = party_service.find_party(party_id)

    if party is None:
        abort(404)

    return party


def _get_article_or_404(article_id):
    article = article_service.find_article(article_id)

    if article is None:
        abort(404)

    return article
