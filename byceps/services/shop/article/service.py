"""
byceps.services.shop.article.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from decimal import Decimal
from typing import Dict, Optional, Sequence, Set

from flask_sqlalchemy import Pagination

from ....database import BaseQuery, db
from ....typing import PartyID

from ...party.models.party import Party

from .models.article import Article, ArticleID, ArticleNumber
from .models.attached_article import AttachedArticle
from .models.compilation import ArticleCompilation, ArticleCompilationItem


def create_article(party_id: PartyID, item_number: ArticleNumber,
                   description: str, price: Decimal, tax_rate: Decimal,
                   quantity: int) -> Article:
    """Create an article."""
    article = Article(party_id, item_number, description, price, tax_rate,
                      quantity)

    db.session.add(article)
    db.session.commit()

    return article


def update_article(article: Article, description: str, price: Decimal,
                   tax_rate: Decimal, available_from: Optional[datetime],
                   available_until: Optional[datetime], quantity: int,
                   max_quantity_per_order: int, not_directly_orderable: bool,
                   requires_separate_order: bool, shipping_required: bool
                  ) -> None:
    """Update the article."""
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


def attach_article(article_to_attach: Article, quantity: int,
                   article_to_attach_to: Article) -> None:
    """Attach an article to another article."""
    attached_article = AttachedArticle(article_to_attach, quantity,
                                       article_to_attach_to)

    db.session.add(attached_article)
    db.session.commit()


def count_articles_for_party(party_id: PartyID) -> int:
    """Return the number of articles that are assigned to that party."""
    return Article.query \
        .for_party_id(party_id) \
        .count()


def unattach_article(attached_article: Article) -> None:
    """Unattach an article from another."""
    db.session.delete(attached_article)
    db.session.commit()


def find_article(article_id: ArticleID) -> Optional[Article]:
    """Return the article with that ID, or `None` if not found."""
    return Article.query.get(article_id)


def find_article_with_details(article_id: ArticleID) -> Optional[Article]:
    """Return the article with that ID, or `None` if not found."""
    return Article.query \
        .options(
            db.joinedload('party'),
            db.joinedload('articles_attached_to').joinedload('article'),
            db.joinedload('attached_articles').joinedload('article'),
        ) \
        .get(article_id)


def find_attached_article(attached_article_id) -> Optional[AttachedArticle]:
    """Return the attached article with that ID, or `None` if not found."""
    return AttachedArticle.query.get(attached_article_id)


def get_article_count_by_party_id() -> Dict[PartyID, int]:
    """Return article count (including 0) per party, indexed by party ID."""
    return dict(db.session \
        .query(
            Party.id,
            db.func.count(Article.party_id)
        ) \
        .outerjoin(Article) \
        .group_by(Party.id) \
        .all())


def get_articles_by_numbers(article_numbers: Set[ArticleNumber]
                           ) -> Sequence[Article]:
    """Return the articles with those numbers."""
    if not article_numbers:
        return []

    return Article.query \
        .filter(Article.item_number.in_(article_numbers)) \
        .all()


def get_articles_for_party(party_id: PartyID) -> Sequence[Article]:
    """Return all articles for that party, ordered by article number."""
    return _get_articles_for_party_query(party_id) \
        .all()


def get_articles_for_party_paginated(party_id: PartyID, page: int, per_page: int
                                    ) -> Pagination:
    """Return all articles for that party, ordered by article number."""
    return _get_articles_for_party_query(party_id) \
        .paginate(page, per_page)


def _get_articles_for_party_query(party_id: PartyID) -> BaseQuery:
    return Article.query \
        .for_party_id(party_id) \
        .order_by(Article.item_number)


def get_article_compilation_for_orderable_articles(party_id: PartyID
                                                  ) -> ArticleCompilation:
    """Return a compilation of the articles which can be ordered for
    that party, less the ones that are only orderable in a dedicated
    order.
    """
    orderable_articles = Article.query \
        .for_party_id(party_id) \
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


def get_article_compilation_for_single_article(article: Article, *,
                                               fixed_quantity: Optional[int]=None
                                              ) -> ArticleCompilation:
    """Return a compilation built from just the given article plus the
    articles attached to it (if any).
    """
    compilation = ArticleCompilation()

    compilation.append(
        ArticleCompilationItem(article, fixed_quantity=fixed_quantity))

    _add_attached_articles(compilation, article.attached_articles)

    return compilation


def _add_attached_articles(compilation: ArticleCompilation,
                           attached_articles: Sequence[AttachedArticle]
                          ) -> None:
    """Add the attached articles to the compilation."""
    for attached_article in attached_articles:
        compilation.append(
            ArticleCompilationItem(attached_article.article,
                                   fixed_quantity=attached_article.quantity))


def get_attachable_articles(article: Article) -> Sequence[Article]:
    """Return the articles that can be attached to that article."""
    attached_articles = {attached.article for attached in article.attached_articles}

    unattachable_articles = {article} | attached_articles

    unattachable_article_ids = {article.id for article in unattachable_articles}

    return Article.query \
        .for_party_id(article.party.id) \
        .filter(db.not_(Article.id.in_(unattachable_article_ids))) \
        .order_by(Article.item_number) \
        .all()
