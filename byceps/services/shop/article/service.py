"""
byceps.services.shop.article.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Sequence, Set, Tuple

from ....database import BaseQuery, db, Pagination

from ..order.models.order import Order as DbOrder
from ..order.models.order_item import OrderItem as DbOrderItem
from ..order.transfer.models import PaymentState
from ..shop.models import Shop as DbShop
from ..shop.transfer.models import ShopID

from .models.article import Article as DbArticle
from .models.attached_article import AttachedArticle as DbAttachedArticle
from .models.compilation import ArticleCompilation, ArticleCompilationItem
from .transfer.models import (
    Article,
    ArticleID,
    ArticleNumber,
    AttachedArticleID,
)


class UnknownArticleId(ValueError):
    pass


def create_article(
    shop_id: ShopID,
    item_number: ArticleNumber,
    description: str,
    price: Decimal,
    tax_rate: Decimal,
    quantity: int,
) -> Article:
    """Create an article."""
    article = DbArticle(
        shop_id, item_number, description, price, tax_rate, quantity
    )

    db.session.add(article)
    db.session.commit()

    return _db_entity_to_article(article)


def update_article(
    article_id: ArticleID,
    description: str,
    price: Decimal,
    tax_rate: Decimal,
    available_from: Optional[datetime],
    available_until: Optional[datetime],
    quantity: int,
    max_quantity_per_order: int,
    not_directly_orderable: bool,
    requires_separate_order: bool,
    shipping_required: bool,
) -> Article:
    """Update the article."""
    article = _get_db_article(article_id)

    article.description = description
    article.price = price
    article.tax_rate = tax_rate
    article.available_from = available_from
    article.available_until = available_until
    article.quantity = quantity
    article.max_quantity_per_order = max_quantity_per_order
    article.not_directly_orderable = not_directly_orderable
    article.requires_separate_order = requires_separate_order
    article.shipping_required = shipping_required

    db.session.commit()

    return _db_entity_to_article(article)


def attach_article(
    article_number_to_attach: ArticleNumber,
    quantity: int,
    article_number_to_attach_to: ArticleNumber,
) -> None:
    """Attach an article to another article."""
    attached_article = DbAttachedArticle(
        article_number_to_attach, quantity, article_number_to_attach_to
    )

    db.session.add(attached_article)
    db.session.commit()


def unattach_article(attached_article_id: AttachedArticleID) -> None:
    """Unattach an article from another."""
    db.session.query(DbAttachedArticle) \
        .filter_by(id=attached_article_id) \
        .delete()

    db.session.commit()


def increase_quantity(
    article_id: ArticleID, quantity_to_increase_by: int, *, commit: bool = True
) -> None:
    """Increase article quantity by the given value."""
    db.session.query(DbArticle) \
        .filter_by(id=article_id) \
        .update({'quantity': DbArticle.quantity + quantity_to_increase_by})

    if commit:
        db.session.commit()


def decrease_quantity(
    article_id: ArticleID, quantity_to_decrease_by: int, *, commit: bool = True
) -> None:
    """Decrease article quantity by the given value."""
    db.session.query(DbArticle) \
        .filter_by(id=article_id) \
        .update({'quantity': DbArticle.quantity - quantity_to_decrease_by})

    if commit:
        db.session.commit()


def delete_article(article_id: ArticleID) -> None:
    """Delete an article."""
    db.session.query(DbArticle) \
        .filter_by(id=article_id) \
        .delete()

    db.session.commit()


def find_article(article_id: ArticleID) -> Optional[Article]:
    """Return the article with that ID, or `None` if not found."""
    article = find_db_article(article_id)

    if article is None:
        return None

    return _db_entity_to_article(article)


def get_article(article_id: ArticleID) -> Article:
    """Return the article with that ID.

    Raise an exception if not found.
    """
    article = find_article(article_id)

    if article is None:
        raise UnknownArticleId(article_id)

    return article


def find_db_article(article_id: ArticleID) -> Optional[DbArticle]:
    """Return the database entity for the article with that ID, or
    `None` if not found.
    """
    return DbArticle.query.get(article_id)


def _get_db_article(article_id: ArticleID) -> DbArticle:
    """Return the database entity for the article with that id.

    Raise an exception if not found.
    """
    article = find_db_article(article_id)

    if article is None:
        raise UnknownArticleId(article_id)

    return article


def find_article_with_details(article_id: ArticleID) -> Optional[DbArticle]:
    """Return the article with that ID, or `None` if not found."""
    return DbArticle.query \
        .options(
            db.joinedload('articles_attached_to').joinedload('article'),
            db.joinedload('attached_articles').joinedload('article'),
        ) \
        .get(article_id)


def find_attached_article(
    attached_article_id: AttachedArticleID,
) -> Optional[DbAttachedArticle]:
    """Return the attached article with that ID, or `None` if not found."""
    return DbAttachedArticle.query.get(attached_article_id)


def get_articles_by_numbers(
    article_numbers: Set[ArticleNumber]
) -> Set[Article]:
    """Return the articles with those numbers."""
    if not article_numbers:
        return []

    rows = DbArticle.query \
        .filter(DbArticle.item_number.in_(article_numbers)) \
        .all()

    return {_db_entity_to_article(row) for row in rows}


def get_articles_for_shop(shop_id: ShopID) -> Sequence[Article]:
    """Return all articles for that shop, ordered by article number."""
    rows = _get_articles_for_shop_query(shop_id) \
        .all()

    return [_db_entity_to_article(row) for row in rows]


def get_articles_for_shop_paginated(
    shop_id: ShopID, page: int, per_page: int
) -> Pagination:
    """Return all articles for that shop, ordered by article number."""
    return _get_articles_for_shop_query(shop_id) \
        .paginate(page, per_page)


def _get_articles_for_shop_query(shop_id: ShopID) -> BaseQuery:
    return DbArticle.query \
        .for_shop(shop_id) \
        .order_by(DbArticle.item_number)


def get_article_compilation_for_orderable_articles(
    shop_id: ShopID,
) -> ArticleCompilation:
    """Return a compilation of the articles which can be ordered from
    that shop, less the ones that are only orderable in a dedicated
    order.
    """
    orderable_articles = DbArticle.query \
        .for_shop(shop_id) \
        .filter_by(not_directly_orderable=False) \
        .filter_by(requires_separate_order=False) \
        .currently_available() \
        .order_by(DbArticle.description) \
        .all()

    compilation = ArticleCompilation()

    for article in orderable_articles:
        compilation.append(
            ArticleCompilationItem(_db_entity_to_article(article))
        )

        _add_attached_articles(compilation, article.attached_articles)

    return compilation


def get_article_compilation_for_single_article(
    article_id: ArticleID, *, fixed_quantity: Optional[int] = None
) -> ArticleCompilation:
    """Return a compilation built from just the given article plus the
    articles attached to it (if any).
    """
    article = _get_db_article(article_id)

    compilation = ArticleCompilation()

    compilation.append(
        ArticleCompilationItem(
            _db_entity_to_article(article), fixed_quantity=fixed_quantity
        )
    )

    _add_attached_articles(compilation, article.attached_articles)

    return compilation


def _add_attached_articles(
    compilation: ArticleCompilation,
    attached_articles: Sequence[DbAttachedArticle],
) -> None:
    """Add the attached articles to the compilation."""
    for attached_article in attached_articles:
        compilation.append(
            ArticleCompilationItem(
                _db_entity_to_article(attached_article.article),
                fixed_quantity=attached_article.quantity,
            )
        )


def get_attachable_articles(article_id: ArticleID) -> Set[Article]:
    """Return the articles that can be attached to that article."""
    article = _get_db_article(article_id)

    attached_articles = {
        attached.article for attached in article.attached_articles
    }

    unattachable_articles = {article}.union(attached_articles)

    unattachable_article_ids = {article.id for article in unattachable_articles}

    rows = DbArticle.query \
        .for_shop(article.shop_id) \
        .filter(db.not_(DbArticle.id.in_(unattachable_article_ids))) \
        .order_by(DbArticle.item_number) \
        .all()

    return {_db_entity_to_article(row) for row in rows}


def is_article_available_now(article: Article) -> bool:
    """Return `True` if the article is available at this moment in time."""
    start = article.available_from
    end = article.available_until

    now = datetime.utcnow()

    return (start is None or start <= now) and (end is None or now < end)


def sum_ordered_articles_by_payment_state(
    shop_ids: Set[ShopID],
) -> List[Tuple[ShopID, ArticleNumber, str, PaymentState, int]]:
    """Sum ordered articles for those shops, grouped by order payment state."""
    subquery = db.session \
        .query(
            DbOrderItem.article_number,
            DbOrder._payment_state.label('payment_state'),
            db.func.sum(DbOrderItem.quantity).label('quantity')
        ) \
        .join(DbOrder) \
        .group_by(DbOrderItem.article_number, DbOrder._payment_state) \
        .subquery()

    rows = db.session \
        .query(
            DbArticle.shop_id,
            DbArticle.item_number,
            DbArticle.description,
            subquery.c.payment_state,
            subquery.c.quantity
        ) \
        .outerjoin(subquery,
            db.and_(DbArticle.item_number == subquery.c.article_number)) \
        .filter(DbArticle.shop_id.in_(shop_ids)) \
        .order_by(DbArticle.item_number, subquery.c.payment_state) \
        .all()

    shop_ids_and_article_numbers_and_descriptions = {
        (row[0], row[1], row[2]) for row in rows
    }  # Remove duplicates.

    quantities = {}

    for (
        shop_id,
        article_number,
        description,
        payment_state_name,
        quantity,
    ) in rows:
        if payment_state_name is None:
            continue

        payment_state = PaymentState[payment_state_name]
        key = (shop_id, article_number, description, payment_state)

        quantities[key] = quantity

    def generate():
        for shop_id, article_number, description in sorted(
            shop_ids_and_article_numbers_and_descriptions
        ):
            for payment_state in PaymentState:
                key = (shop_id, article_number, description, payment_state)
                quantity = quantities.get(key, 0)

                yield shop_id, article_number, description, payment_state, quantity

    return list(generate())


def _db_entity_to_article(article: DbArticle) -> Article:
    return Article(
        article.id,
        article.shop_id,
        article.item_number,
        article.description,
        article.price,
        article.tax_rate,
        article.available_from,
        article.available_until,
        article.quantity,
        article.max_quantity_per_order,
        article.not_directly_orderable,
        article.requires_separate_order,
        article.shipping_required,
    )
