# -*- coding: utf-8 -*-

"""
byceps.blueprints.shop.models.article
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from decimal import Decimal

from flask import g
from Ranger import Range
from Ranger.src.Range.Cut import Cut

from ....database import BaseQuery, db, generate_uuid
from ....util.instances import ReprBuilder

from ...party.models import Party


class ArticleQuery(BaseQuery):

    def for_current_party(self):
        return self.for_party(g.party)

    def for_party(self, party):
        return self.filter_by(party_id=party.id)

    def currently_available(self):
        """Select only articles that are available in between the
        temporal boundaries for this article, if specified.
        """
        now = datetime.now()

        return self \
            .filter(db.or_(
                Article.available_from == None,
                now >= Article.available_from
            )) \
            .filter(db.or_(
                Article.available_until == None,
                now < Article.available_until
            ))


class Article(db.Model):
    """An article that can be bought."""
    __tablename__ = 'shop_articles'
    __table_args__ = (
        db.UniqueConstraint('party_id', 'description'),
    )
    query_class = ArticleQuery

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    party_id = db.Column(db.Unicode(20), db.ForeignKey('parties.id'), index=True, nullable=False)
    party = db.relationship(Party)
    item_number = db.Column(db.Unicode(20), unique=True, nullable=False)
    description = db.Column(db.Unicode(80), nullable=False)
    price = db.Column(db.Numeric(6, 2), nullable=False)
    tax_rate = db.Column(db.Numeric(3, 3), nullable=False)
    available_from = db.Column(db.DateTime, nullable=True)
    available_until = db.Column(db.DateTime, nullable=True)
    quantity = db.Column(db.Integer, nullable=False)
    max_quantity_per_order = db.Column(db.Integer, nullable=True)
    not_directly_orderable = db.Column(db.Boolean, default=False, nullable=False)
    requires_separate_order = db.Column(db.Boolean, default=False, nullable=False)

    def __init__(self, party, item_number, description, price, tax_rate,
                 quantity, *, available_from=None, available_until=None):
        self.party = party
        self.item_number = item_number
        self.description = description
        self.price = price
        self.tax_rate = tax_rate
        self.available_from = available_from
        self.available_until = available_until
        self.quantity = quantity

    @property
    def tax_rate_as_percentage(self):
        # Keep a digit after the decimal point in case
        # the tax rate is a fractional number.
        percentage = (self.tax_rate * 100).quantize(Decimal('.0'))
        return str(percentage).replace('.', ',')

    @property
    def availability_range(self):
        """Assemble the date/time range of the articles availability."""
        start = self.available_from
        end = self.available_until

        if start:
            if end:
                return Range.closedOpen(start, end)
            else:
                return Range.atLeast(start)
        else:
            if end:
                return Range.lessThan(end)
            else:
                return range_all(datetime)

    @property
    def is_available(self):
        """Return `True` if the article is available at this moment in time."""
        now = datetime.now()
        return self.availability_range.contains(now)

    def __repr__(self):
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add('party', self.party_id) \
            .add_with_lookup('item_number') \
            .add_with_lookup('description') \
            .add_with_lookup('quantity') \
            .build()


def range_all(theType):
    """Create a range than contains every value of the given type."""
    return Range(
        Cut.belowAll(theType=theType),
        Cut.aboveAll(theType=theType))


# -------------------------------------------------------------------- #
# articles attached to articles


class AttachedArticle(db.Model):
    """An article that is attached to another article."""
    __tablename__ = 'shop_attached_articles'
    __table_args__ = (
        db.UniqueConstraint('article_number', 'attached_to_article_number'),
    )

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    article_number = db.Column(db.Unicode(20),
                               db.ForeignKey('shop_articles.item_number'),
                               nullable=False, index=True)
    article = db.relationship(Article, foreign_keys=[article_number],
                              backref=db.backref('articles_attached_to', collection_class=set))
    quantity = db.Column(db.Integer, nullable=False)
    attached_to_article_number = db.Column(db.Unicode(20),
                                           db.ForeignKey('shop_articles.item_number'),
                                           nullable=False, index=True)
    attached_to_article = db.relationship(Article, foreign_keys=[attached_to_article_number],
                                          backref=db.backref('attached_articles', collection_class=set))

    def __init__(self, article, quantity, attached_to_article):
        self.article = article
        self.quantity = quantity
        self.attached_to_article = attached_to_article


# -------------------------------------------------------------------- #
# article compilation


class ArticleCompilation(object):

    def __init__(self):
        self._items = []

    def append(self, item):
        self._items.append(item)

    def __iter__(self):
        return iter(self._items)

    def is_empty(self):
        return not self._items


class ArticleCompilationItem(object):

    def __init__(self, article, *, fixed_quantity=None):
        if (fixed_quantity is not None) and fixed_quantity < 1:
            raise ValueError(
                'Fixed quantity, if given, must be a positive number.')

        self.article = article
        self.fixed_quantity = fixed_quantity

    def has_fixed_quantity(self):
        return self.fixed_quantity is not None
