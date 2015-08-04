# -*- coding: utf-8 -*-

"""
byceps.blueprints.shop.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...database import db

from .models import Article, ArticleCompilation, ArticleCompilationItem, \
    Order, PartySequence, PartySequencePurpose
from .signals import order_placed


def get_article_compilation_for_orderable_articles():
    """Return a compilation of the articles which can be ordered for
    the current party, less the ones that are only orderable in a
    dedicated order.
    """
    orderable_articles = Article.query \
        .for_current_party() \
        .filter_by(not_directly_orderable=False) \
        .filter_by(requires_separate_order=False) \
        .currently_available() \
        .order_by(Article.description) \
        .all()

    compilation = ArticleCompilation()

    for article in orderable_articles:
        compilation.append(ArticleCompilationItem(article))

        _add_attached_articles(compilation, article.attached_articles)

    return compilation


def get_article_compilation_for_single_article(article, *, fixed_quantity=None):
    """Return a compilation built from just the given article plus the
    articles attached to it (if any).
    """
    compilation = ArticleCompilation()

    compilation.append(
        ArticleCompilationItem(article, fixed_quantity=fixed_quantity))

    _add_attached_articles(compilation, article.attached_articles)

    return compilation


def _add_attached_articles(compilation, attached_articles):
    """Add the attached articles to the compilation."""
    for attached_article in attached_articles:
        compilation.append(
            ArticleCompilationItem(attached_article.article,
                                   fixed_quantity=attached_article.quantity))


def generate_article_number(party):
    """Generate and reserve an unused, unique article number for this party."""
    article_serial_number = _get_next_serial_number(party,
                                                    PartySequencePurpose.article)

    return '{}-{:02d}-A{:05d}'.format(
        party.brand.code,
        party.number,
        article_serial_number)


def generate_order_number(party):
    """Generate and reserve an unused, unique order number for this party."""
    order_serial_number = _get_next_serial_number(party,
                                                  PartySequencePurpose.order)

    return '{}-{:02d}-B{:05d}'.format(
        party.brand.code,
        party.number,
        order_serial_number)


def _get_next_serial_number(party, purpose):
    """Calculate and reserve the next serial number for the party and purpose."""
    sequence = PartySequence.query \
        .filter_by(party=party) \
        .filter_by(_purpose=purpose.name) \
        .with_for_update() \
        .one()

    sequence.value = PartySequence.value + 1
    db.session.commit()
    return sequence.value


def create_order(party, orderer, cart):
    """Create an order of one or more articles."""
    order_number = generate_order_number(party)

    order = build_order(party, order_number, orderer)
    add_items_from_cart_to_order(cart, order)
    db.session.commit()

    order_placed.send(None, order=order)

    return order


def build_order(party, order_number, orderer):
    """Create an order of one or more articles."""
    order = Order(
        party=party,
        order_number=order_number,
        placed_by=orderer.user,
        first_names=orderer.first_names,
        last_name=orderer.last_name,
        date_of_birth=orderer.date_of_birth,
        zip_code=orderer.zip_code,
        city=orderer.city,
        street=orderer.street,
    )
    db.session.add(order)
    return order


def add_items_from_cart_to_order(cart, order):
    """Add the items from the cart to the order."""
    for article_item in cart.get_items():
        article = article_item.article
        quantity = article_item.quantity

        article.quantity -= quantity

        order_item = order.add_item(article, quantity)
        db.session.add(order_item)


def get_orders_placed_by_user(user):
    """Return orders placed by the user."""
    return Order.query \
        .placed_by(user) \
        .order_by(Order.created_at.desc()) \
        .all()


def has_user_placed_orders(user):
    """Return `True` if the user has placed orders for the current party."""
    orders_total = Order.query \
        .for_current_party() \
        .filter_by(placed_by=user) \
        .count()
    return orders_total > 0
