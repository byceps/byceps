"""
byceps.services.shop.article.article_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from typing import Iterable, Optional

from moneyed import Money
from sqlalchemy import delete, select, update
from sqlalchemy.sql import Select

from byceps.database import db, paginate, Pagination
from byceps.services.shop.cart.models import Cart
from byceps.services.shop.order.dbmodels.line_item import DbLineItem
from byceps.services.shop.order.dbmodels.order import DbOrder
from byceps.services.shop.order.models.order import PaymentState
from byceps.services.shop.shop.models import ShopID
from byceps.services.ticketing.models.ticket import TicketCategoryID

from .dbmodels.article import DbArticle
from .dbmodels.attached_article import DbAttachedArticle
from .models import (
    Article,
    ArticleCompilation,
    ArticleCompilationItem,
    ArticleID,
    ArticleNumber,
    ArticleType,
    ArticleTypeParams,
    AttachedArticleID,
)


class UnknownArticleId(ValueError):
    pass


def create_article(
    shop_id: ShopID,
    item_number: ArticleNumber,
    type_: ArticleType,
    description: str,
    price: Money,
    tax_rate: Decimal,
    total_quantity: int,
    max_quantity_per_order: int,
    processing_required: bool,
    *,
    type_params: Optional[ArticleTypeParams] = None,
    available_from: Optional[datetime] = None,
    available_until: Optional[datetime] = None,
    not_directly_orderable: bool = False,
    separate_order_required: bool = False,
) -> Article:
    """Create an article."""
    db_article = DbArticle(
        shop_id,
        item_number,
        type_,
        description,
        price,
        tax_rate,
        total_quantity,
        max_quantity_per_order,
        processing_required,
        type_params=type_params,
        available_from=available_from,
        available_until=available_until,
        not_directly_orderable=not_directly_orderable,
        separate_order_required=separate_order_required,
    )

    db.session.add(db_article)
    db.session.commit()

    return _db_entity_to_article(db_article)


def create_ticket_article(
    shop_id: ShopID,
    item_number: ArticleNumber,
    description: str,
    price: Money,
    tax_rate: Decimal,
    total_quantity: int,
    max_quantity_per_order: int,
    ticket_category_id: TicketCategoryID,
    *,
    available_from: Optional[datetime] = None,
    available_until: Optional[datetime] = None,
    not_directly_orderable: bool = False,
    separate_order_required: bool = False,
) -> Article:
    """Create an article that represents a ticket."""
    type_params: ArticleTypeParams = {
        'ticket_category_id': str(ticket_category_id),
    }
    processing_required = True

    return create_article(
        shop_id,
        item_number,
        ArticleType.ticket,
        description,
        price,
        tax_rate,
        total_quantity,
        max_quantity_per_order,
        processing_required,
        type_params=type_params,
        available_from=available_from,
        available_until=available_until,
        not_directly_orderable=not_directly_orderable,
        separate_order_required=separate_order_required,
    )


def create_ticket_bundle_article(
    shop_id: ShopID,
    item_number: ArticleNumber,
    description: str,
    price: Money,
    tax_rate: Decimal,
    total_quantity: int,
    max_quantity_per_order: int,
    ticket_category_id: TicketCategoryID,
    ticket_quantity: int,
    *,
    available_from: Optional[datetime] = None,
    available_until: Optional[datetime] = None,
    not_directly_orderable: bool = False,
    separate_order_required: bool = False,
) -> Article:
    """Create an article that represents a ticket bundle."""
    type_params: ArticleTypeParams = {
        'ticket_category_id': str(ticket_category_id),
        'ticket_quantity': ticket_quantity,
    }
    processing_required = True

    return create_article(
        shop_id,
        item_number,
        ArticleType.ticket_bundle,
        description,
        price,
        tax_rate,
        total_quantity,
        max_quantity_per_order,
        processing_required,
        type_params=type_params,
        available_from=available_from,
        available_until=available_until,
        not_directly_orderable=not_directly_orderable,
        separate_order_required=separate_order_required,
    )


def update_article(
    article_id: ArticleID,
    description: str,
    price: Money,
    tax_rate: Decimal,
    available_from: Optional[datetime],
    available_until: Optional[datetime],
    total_quantity: int,
    max_quantity_per_order: int,
    not_directly_orderable: bool,
    separate_order_required: bool,
) -> Article:
    """Update the article."""
    db_article = _get_db_article(article_id)

    db_article.description = description
    db_article.price_amount = price.amount
    db_article.price_currency = price.currency
    db_article.tax_rate = tax_rate
    db_article.available_from = available_from
    db_article.available_until = available_until
    db_article.total_quantity = total_quantity
    db_article.max_quantity_per_order = max_quantity_per_order
    db_article.not_directly_orderable = not_directly_orderable
    db_article.separate_order_required = separate_order_required

    db.session.commit()

    return _db_entity_to_article(db_article)


def attach_article(
    article_id_to_attach: ArticleID,
    quantity: int,
    article_id_to_attach_to: ArticleID,
) -> None:
    """Attach an article to another article."""
    db_attached_article = DbAttachedArticle(
        article_id_to_attach, quantity, article_id_to_attach_to
    )

    db.session.add(db_attached_article)
    db.session.commit()


def unattach_article(attached_article_id: AttachedArticleID) -> None:
    """Unattach an article from another."""
    db.session.execute(
        delete(DbAttachedArticle).filter_by(id=attached_article_id)
    )
    db.session.commit()


def increase_quantity(
    article_id: ArticleID, quantity_to_increase_by: int, *, commit: bool = True
) -> None:
    """Increase article quantity by the given value."""
    db.session.execute(
        update(DbArticle)
        .where(DbArticle.id == article_id)
        .values(quantity=DbArticle.quantity + quantity_to_increase_by)
    )

    if commit:
        db.session.commit()


def decrease_quantity(
    article_id: ArticleID, quantity_to_decrease_by: int, *, commit: bool = True
) -> None:
    """Decrease article quantity by the given value."""
    db.session.execute(
        update(DbArticle)
        .where(DbArticle.id == article_id)
        .values(quantity=DbArticle.quantity - quantity_to_decrease_by)
    )

    if commit:
        db.session.commit()


def delete_article(article_id: ArticleID) -> None:
    """Delete an article."""
    db.session.execute(delete(DbArticle).filter_by(id=article_id))
    db.session.commit()


def find_article(article_id: ArticleID) -> Optional[Article]:
    """Return the article with that ID, or `None` if not found."""
    db_article = find_db_article(article_id)

    if db_article is None:
        return None

    return _db_entity_to_article(db_article)


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
    return db.session.get(DbArticle, article_id)


def _get_db_article(article_id: ArticleID) -> DbArticle:
    """Return the database entity for the article with that id.

    Raise an exception if not found.
    """
    db_article = find_db_article(article_id)

    if db_article is None:
        raise UnknownArticleId(article_id)

    return db_article


def find_article_with_details(article_id: ArticleID) -> Optional[DbArticle]:
    """Return the article with that ID, or `None` if not found."""
    return (
        db.session.execute(
            select(DbArticle)
            .options(
                db.joinedload(DbArticle.articles_attached_to).joinedload(
                    DbAttachedArticle.article
                ),
                db.joinedload(DbArticle.attached_articles).joinedload(
                    DbAttachedArticle.article
                ),
            )
            .filter_by(id=article_id)
        )
        .unique()
        .scalar_one_or_none()
    )


def find_attached_article(
    attached_article_id: AttachedArticleID,
) -> Optional[DbAttachedArticle]:
    """Return the attached article with that ID, or `None` if not found."""
    return db.session.get(DbAttachedArticle, attached_article_id)


def get_attached_articles_for_articles(
    article_ids: set[ArticleID],
) -> dict[ArticleID, list[DbAttachedArticle]]:
    """Return the attached article with that ID, or `None` if not found."""
    if not article_ids:
        return {}

    rows = db.session.execute(
        select(DbAttachedArticle.attached_to_article_id, DbAttachedArticle)
        .filter(DbAttachedArticle.attached_to_article_id.in_(article_ids))
        .options(db.joinedload(DbAttachedArticle.article))
    ).all()

    attached_articles_by_attached_to_article_id = defaultdict(list)
    for attached_to_article_id, db_attached_article in rows:
        attached_articles_by_attached_to_article_id[
            attached_to_article_id
        ].append(db_attached_article)

    return attached_articles_by_attached_to_article_id


def get_article_by_number(article_number: ArticleNumber) -> Article:
    """Return the article with that item number."""
    db_article = db.session.execute(
        select(DbArticle).filter_by(item_number=article_number)
    ).scalar_one()

    return _db_entity_to_article(db_article)


def get_articles(article_ids: set[ArticleID]) -> list[Article]:
    """Return the articles with those IDs."""
    if not article_ids:
        return list()

    db_articles = db.session.scalars(
        select(DbArticle).filter(DbArticle.id.in_(article_ids))
    ).all()

    return [_db_entity_to_article(db_article) for db_article in db_articles]


def get_articles_for_shop(shop_id: ShopID) -> list[Article]:
    """Return all articles for that shop, ordered by article number."""
    db_articles = db.session.scalars(
        select(DbArticle)
        .filter_by(shop_id=shop_id)
        .order_by(DbArticle.item_number)
    ).all()

    return [_db_entity_to_article(db_article) for db_article in db_articles]


def get_articles_for_shop_paginated(
    shop_id: ShopID,
    page: int,
    per_page: int,
    *,
    search_term=None,
) -> Pagination:
    """Return all articles for that shop, paginated.

    Ordered by article number, reversed.
    """
    stmt = (
        select(DbArticle)
        .filter_by(shop_id=shop_id)
        .order_by(DbArticle.item_number.desc())
    )

    if search_term:
        stmt = _filter_by_search_term(stmt, search_term)

    return paginate(stmt, page, per_page)


def _filter_by_search_term(stmt: Select, search_term: str) -> Select:
    terms = search_term.split(' ')
    clauses = map(_generate_search_clauses_for_term, terms)

    return stmt.filter(db.and_(*clauses))


def _generate_search_clauses_for_term(search_term: str) -> Select:
    ilike_pattern = f'%{search_term}%'

    return db.or_(
        DbArticle.item_number.ilike(ilike_pattern),
        DbArticle.description.ilike(ilike_pattern),
    )


def get_article_compilation_for_orderable_articles(
    shop_id: ShopID,
) -> ArticleCompilation:
    """Return a compilation of the articles which can be ordered from
    that shop, less the ones that are only orderable in a dedicated
    order.
    """
    now = datetime.utcnow()

    db_orderable_articles = db.session.scalars(
        select(DbArticle)
        .filter_by(shop_id=shop_id)
        .filter_by(not_directly_orderable=False)
        .filter_by(separate_order_required=False)
        # Select only articles that are available in between the
        # temporal boundaries for this article, if specified.
        .filter(
            db.or_(
                DbArticle.available_from.is_(None),
                now >= DbArticle.available_from,
            )
        )
        .filter(
            db.or_(
                DbArticle.available_until.is_(None),
                now < DbArticle.available_until,
            )
        )
        .order_by(DbArticle.description)
    ).all()

    compilation = ArticleCompilation()

    for db_article in db_orderable_articles:
        compilation = compilation.append(
            ArticleCompilationItem(_db_entity_to_article(db_article))
        )

        compilation = _add_attached_articles(
            compilation, db_article.attached_articles
        )

    return compilation


def get_article_compilation_for_single_article(
    article_id: ArticleID,
) -> ArticleCompilation:
    """Return a compilation built from just the given article (with a
    quantity of one) plus the articles attached to it (if any).
    """
    db_article = _get_db_article(article_id)

    compilation = ArticleCompilation()

    compilation = compilation.append(
        ArticleCompilationItem(
            _db_entity_to_article(db_article), fixed_quantity=1
        )
    )

    compilation = _add_attached_articles(
        compilation, db_article.attached_articles
    )

    return compilation


def get_article_compilations_for_single_articles(
    article_ids: set[ArticleID],
) -> dict[ArticleID, ArticleCompilation]:
    """Return a compilation of the articles (with a quantity of one)
    plus the articles attached to it (if any).
    """
    if not article_ids:
        return {}

    compilations_by_article_id: dict[ArticleID, ArticleCompilation] = {}

    db_articles = db.session.scalars(
        select(DbArticle).filter(DbArticle.id.in_(article_ids))
    ).all()

    attached_articles_by_attached_to_article_id = (
        get_attached_articles_for_articles(article_ids)
    )

    for db_article in db_articles:
        article = _db_entity_to_article(db_article)

        compilation = ArticleCompilation()

        compilation = compilation.append(
            ArticleCompilationItem(article, fixed_quantity=1)
        )

        db_attached_articles = attached_articles_by_attached_to_article_id[
            db_article.id
        ]
        compilation = _add_attached_articles(compilation, db_attached_articles)

        compilations_by_article_id[article.id] = compilation

    return compilations_by_article_id


def _add_attached_articles(
    compilation: ArticleCompilation,
    attached_articles: Iterable[DbAttachedArticle],
) -> ArticleCompilation:
    """Add the attached articles to the compilation."""
    for attached_article in attached_articles:
        compilation = compilation.append(
            ArticleCompilationItem(
                _db_entity_to_article(attached_article.article),
                fixed_quantity=attached_article.quantity,
            )
        )

    return compilation


def get_attachable_articles(article_id: ArticleID) -> list[Article]:
    """Return the articles that can be attached to that article."""
    db_article = _get_db_article(article_id)

    db_attached_articles = {
        db_attached.article for db_attached in db_article.attached_articles
    }

    db_unattachable_articles = {db_article}.union(db_attached_articles)

    unattachable_article_ids = {
        db_article.id for db_article in db_unattachable_articles
    }

    db_articles = db.session.scalars(
        select(DbArticle)
        .filter_by(shop_id=db_article.shop_id)
        .filter(db.not_(DbArticle.id.in_(unattachable_article_ids)))
        .order_by(DbArticle.item_number)
    ).all()

    return [_db_entity_to_article(db_article) for db_article in db_articles]


def is_article_available_now(article: Article) -> bool:
    """Return `True` if the article is available at this moment in time."""
    start = article.available_from
    end = article.available_until

    now = datetime.utcnow()

    return (start is None or start <= now) and (end is None or now < end)


def calculate_article_compilation_total_amount(
    compilation: ArticleCompilation,
) -> Money:
    """Calculate total amount of articles and their attached articles in
    the compilation.
    """
    cart = Cart(compilation._items[0].article.price.currency)
    _copy_article_compilation_to_cart(compilation, cart)
    return cart.calculate_total_amount()


def _copy_article_compilation_to_cart(
    compilation: ArticleCompilation, cart: Cart
) -> None:
    for compilation_item in compilation:
        if compilation_item.fixed_quantity is None:
            raise ValueError(
                'Für einige Artikel ist keine Stückzahl vorgegeben.'
            )

        cart.add_item(compilation_item.article, compilation_item.fixed_quantity)


def sum_ordered_articles_by_payment_state(
    shop_ids: set[ShopID],
) -> list[tuple[ShopID, ArticleNumber, str, PaymentState, int]]:
    """Sum ordered articles for those shops, grouped by order payment state."""
    subquery = (
        select(
            DbLineItem.article_id,
            DbOrder._payment_state.label('payment_state'),
            db.func.sum(DbLineItem.quantity).label('quantity'),
        )
        .join(DbOrder)
        .group_by(DbLineItem.article_id, DbOrder._payment_state)
        .subquery()
    )

    rows = db.session.execute(
        select(
            DbArticle.shop_id,
            DbArticle.item_number,
            DbArticle.description,
            subquery.c.payment_state,
            subquery.c.quantity,
        )
        .outerjoin(
            subquery,
            db.and_(DbArticle.id == subquery.c.article_id),
        )
        .filter(DbArticle.shop_id.in_(shop_ids))
        .order_by(DbArticle.item_number, subquery.c.payment_state)
    ).all()

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


def _db_entity_to_article(db_article: DbArticle) -> Article:
    return Article(
        id=db_article.id,
        shop_id=db_article.shop_id,
        item_number=db_article.item_number,
        type_=db_article.type_,
        type_params=db_article.type_params or {},
        description=db_article.description,
        price=db_article.price,
        tax_rate=db_article.tax_rate,
        available_from=db_article.available_from,
        available_until=db_article.available_until,
        total_quantity=db_article.total_quantity,
        quantity=db_article.quantity,
        max_quantity_per_order=db_article.max_quantity_per_order,
        not_directly_orderable=db_article.not_directly_orderable,
        separate_order_required=db_article.separate_order_required,
        processing_required=db_article.processing_required,
    )
