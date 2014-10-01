# -*- coding: utf-8 -*-

"""
byceps.blueprints.shop.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from collections import namedtuple

from flask import g
from sqlalchemy.ext.hybrid import hybrid_property

from ...database import BaseQuery, db, generate_uuid
from ...util.instances import ReprBuilder

from ..party.models import Party


class EuroAmount(namedtuple('EuroAmount', ['euro', 'cent'])):

    @classmethod
    def from_int(cls, value):
        if value < 0:
            raise ValueError

        euro, cent = divmod(value, 100)
        return cls(euro, cent)

    def to_int(self):
        return (self.euro * 100) + self.cent


class ArticleQuery(BaseQuery):

    def for_current_party(self):
        return self.for_party(g.party)

    def for_party(self, party):
        return self.filter_by(party_id=party.id)


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
    description = db.Column(db.Unicode(80), nullable=False)
    _price = db.Column('price', db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    @hybrid_property
    def price(self):
        return EuroAmount.from_int(self._price)

    @price.setter
    def price(self, amount):
        self._price = amount.to_int()

    def __repr__(self):
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add('party', self.party_id) \
            .add_with_lookup('description') \
            .build()
