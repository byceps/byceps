# -*- coding: utf-8 -*-

"""
byceps.blueprints.shop.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from collections import namedtuple
from datetime import datetime
from enum import Enum

from flask import g
from sqlalchemy.ext.hybrid import hybrid_property

from ...database import BaseQuery, db, generate_uuid
from ...util.instances import ReprBuilder

from ..party.models import Party
from ..user.models import User


class EuroAmount(namedtuple('EuroAmount', ['euro', 'cent'])):

    @classmethod
    def from_int(cls, value):
        if value < 0:
            raise ValueError

        euro, cent = divmod(value, 100)
        return cls(euro, cent)

    def to_int(self):
        return (self.euro * 100) + self.cent

    def to_str(self):
        return '{0.euro:d},{0.cent:02d}'.format(self)


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


PaymentState = Enum('PaymentState', ['open', 'canceled', 'paid'])


class OrderQuery(BaseQuery):

    def for_current_party(self):
        return self.for_party(g.party)

    def for_party(self, party):
        return self.filter_by(party_id=party.id)


class Order(db.Model):
    """An order for articles, placed by a user."""
    __tablename__ = 'shop_orders'
    query_class = OrderQuery

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    party_id = db.Column(db.Unicode(20), db.ForeignKey('parties.id'), index=True, nullable=False)
    party = db.relationship(Party)
    placed_by_id = db.Column(db.Uuid, db.ForeignKey('users.id'), index=True, nullable=False)
    placed_by = db.relationship(User)
    first_names = db.Column(db.Unicode(40), nullable=False)
    last_name = db.Column(db.Unicode(40), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    zip_code = db.Column(db.Unicode(5), nullable=False)
    city = db.Column(db.Unicode(40), nullable=False)
    street = db.Column(db.Unicode(40), nullable=False)
    _payment_state = db.Column('payment_state', db.Unicode(20), nullable=False)

    @hybrid_property
    def payment_state(self):
        return PaymentState[self._payment_state]

    @payment_state.setter
    def payment_state(self, amount):
        assert state is not None
        self._payment_state = state.name

    def __repr__(self):
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add('party', self.party_id) \
            .add('placed_by', self.placed_by.screen_name) \
            .add('payment_state', self.payment_state.name) \
            .build()


class OrderItem(db.Model):
    """An item that belongs to an order."""
    __tablename__ = 'shop_order_items'

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    order_id = db.Column(db.Uuid, db.ForeignKey('shop_orders.id'), index=True, nullable=False)
    order = db.relationship(Order, backref='items')
    article_id = db.Column(db.Uuid, db.ForeignKey('shop_articles.id'), index=True, nullable=False)
    article = db.relationship(Article)
    description = db.Column(db.Unicode(80), nullable=False)
    _price = db.Column('price', db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    @hybrid_property
    def price(self):
        return EuroAmount.from_int(self._price)

    @price.setter
    def price(self, amount):
        self._price = amount.to_int()
