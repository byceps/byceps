# -*- coding: utf-8 -*-

"""
byceps.blueprints.shop.article_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...database import db

from .models.article import Article, ArticleCompilation, \
    ArticleCompilationItem, AttachedArticle


def create_article(party, item_number, description, price, tax_rate, quantity):
    """Create an article."""
    article = Article(party, item_number, description, price, tax_rate,
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


def unattach_article(attached_article):
    """Unattach an article from another."""
    db.session.delete(attached_article)
    db.session.commit()


def find_article(article_id):
    """Return the article with that id, or `None` if not found."""
    return Article.query.get(article_id)


def find_attached_article(attached_article_id):
    """Return the attached article with that id, or `None` if not found."""
    return AttachedArticle.query.get(attached_article_id)


def get_articles_for_party(party):
    """Return all articles for that party, ordered by article number."""
    return _get_articles_for_party_query(party).all()


def get_articles_for_party_paginated(party, page, per_page):
    """Return all articles for that party, ordered by article number."""
    return _get_articles_for_party_query(party).paginate(page, per_page)


def _get_articles_for_party_query(party):
    return Article.query \
        .for_party(party) \
        .order_by(Article.item_number)


def get_article_compilation_for_orderable_articles(party):
    """Return a compilation of the articles which can be ordered for
    that party, less the ones that are only orderable in a dedicated
    order.
    """
    orderable_articles = Article.query \
        .for_party(party) \
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
