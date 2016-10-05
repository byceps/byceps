# -*- coding: utf-8 -*-

"""
byceps.blueprints.shop.article_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...database import db
from ...services.party.models import Party

from .models.article import Article, ArticleCompilation, \
    ArticleCompilationItem, AttachedArticle


def create_article(party_id, item_number, description, price, tax_rate,
                   quantity):
    """Create an article."""
    article = Article(party_id, item_number, description, price, tax_rate,
                      quantity)

    db.session.add(article)
    db.session.commit()

    return article


def update_article(article, description, price, tax_rate, quantity,
                   max_quantity_per_order, not_directly_orderable,
                   requires_separate_order):
    """Update the article."""
    article.description = description
    article.price = price
    article.tax_rate = tax_rate
    article.quantity = quantity
    article.max_quantity_per_order = max_quantity_per_order
    article.not_directly_orderable = not_directly_orderable
    article.requires_separate_order = requires_separate_order

    db.session.commit()


def attach_article(article_to_attach, quantity, article_to_attach_to):
    """Attach an article to another article."""
    attached_article = AttachedArticle(article_to_attach, quantity,
                                       article_to_attach_to)

    db.session.add(attached_article)
    db.session.commit()


def count_articles_for_party(party_id):
    """Return the number of articles that are assigned to that party."""
    return Article.query \
        .for_party_id(party_id) \
        .count()


def unattach_article(attached_article):
    """Unattach an article from another."""
    db.session.delete(attached_article)
    db.session.commit()


def find_article(article_id):
    """Return the article with that id, or `None` if not found."""
    return Article.query.get(article_id)


def find_article_with_details(article_id):
    """Return the article with that ID, or `None` if not found."""
    return Article.query \
        .options(
            db.joinedload('party'),
            db.joinedload('articles_attached_to').joinedload('article'),
            db.joinedload('attached_articles').joinedload('article'),
        ) \
        .get(article_id)


def find_attached_article(attached_article_id):
    """Return the attached article with that id, or `None` if not found."""
    return AttachedArticle.query.get(attached_article_id)


def get_article_count_by_party_id():
    """Return article count (including 0) per party, indexed by party ID."""
    return dict(db.session \
        .query(
            Party.id,
            db.func.count(Article.party_id)
        ) \
        .outerjoin(Article) \
        .group_by(Party.id) \
        .all())


def get_articles_for_party(party_id):
    """Return all articles for that party, ordered by article number."""
    return _get_articles_for_party_query(party_id) \
        .all()


def get_articles_for_party_paginated(party_id, page, per_page):
    """Return all articles for that party, ordered by article number."""
    return _get_articles_for_party_query(party_id) \
        .paginate(page, per_page)


def _get_articles_for_party_query(party_id):
    return Article.query \
        .for_party_id(party_id) \
        .order_by(Article.item_number)


def get_article_compilation_for_orderable_articles(party_id):
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


def get_attachable_articles(article):
    """Return the articles that can be attached to that article."""
    attached_articles = {attached.article for attached in article.attached_articles}

    unattachable_articles = {article} | attached_articles

    unattachable_article_ids = {article.id for article in unattachable_articles}

    return Article.query \
        .for_party_id(article.party.id) \
        .filter(db.not_(Article.id.in_(unattachable_article_ids))) \
        .order_by(Article.item_number) \
        .all()
