# -*- coding: utf-8 -*-

"""
byceps.blueprints.shop.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
"""

from datetime import datetime
from enum import Enum

from flask import g
from Ranger import Range
from Ranger.src.Range.Cut import Cut
from sqlalchemy.ext.hybrid import hybrid_property

from ...database import BaseQuery, db, generate_uuid
from ...util.instances import ReprBuilder
from ...util.money import EuroAmount

from ..party.models import Party
from ..user.models import User


# -------------------------------------------------------------------- #
# articles


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
        db.UniqueConstraint('party_id', 'item_number'),
        db.UniqueConstraint('party_id', 'description'),
    )
    query_class = ArticleQuery

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    party_id = db.Column(db.Unicode(20), db.ForeignKey('parties.id'), index=True, nullable=False)
    party = db.relationship(Party)
    item_number = db.Column(db.Unicode(20), unique=True, nullable=False)
    description = db.Column(db.Unicode(80), nullable=False)
    _price = db.Column('price', db.Integer, nullable=False)
    tax_rate = db.Column(db.Numeric(3, 3), nullable=False)
    available_from = db.Column(db.DateTime, nullable=True)
    available_until = db.Column(db.DateTime, nullable=True)
    quantity = db.Column(db.Integer, nullable=False)
    max_quantity_per_order = db.Column(db.Integer, nullable=True)
    requires_separate_order = db.Column(db.Boolean, default=False, nullable=False)

    def __init__(self, party, item_number, description, price, tax_rate,
                 quantity, *, available_from=None, available_until=None):
        self.party = party
        self.item_number = item_number
        self.description = description
        self._price = price.to_int()
        self.tax_rate = tax_rate
        self.available_from = available_from
        self.available_until = available_until
        self.quantity = quantity

    @hybrid_property
    def price(self):
        return EuroAmount.from_int(int(self._price))

    @price.setter
    def price(self, amount):
        self._price = amount.to_int()

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
# orders


PaymentState = Enum('PaymentState', ['open', 'canceled', 'paid'])


class OrderQuery(BaseQuery):

    def for_current_party(self):
        return self.for_party(g.party)

    def for_party(self, party):
        return self.filter_by(party_id=party.id)

    def placed_by(self, user):
        return self.filter_by(placed_by=user)


class Order(db.Model):
    """An order for articles, placed by a user."""
    __tablename__ = 'shop_orders'
    query_class = OrderQuery
    __table_args__ = (
        db.UniqueConstraint('party_id', 'order_number'),
    )

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    party_id = db.Column(db.Unicode(20), db.ForeignKey('parties.id'), index=True, nullable=False)
    party = db.relationship(Party)
    order_number = db.Column(db.Unicode(13), index=True, nullable=False)
    placed_by_id = db.Column(db.Uuid, db.ForeignKey('users.id'), index=True, nullable=False)
    placed_by = db.relationship(User, foreign_keys=[placed_by_id])
    first_names = db.Column(db.Unicode(40), nullable=False)
    last_name = db.Column(db.Unicode(40), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    zip_code = db.Column(db.Unicode(5), nullable=False)
    city = db.Column(db.Unicode(40), nullable=False)
    street = db.Column(db.Unicode(40), nullable=False)
    _payment_state = db.Column('payment_state', db.Unicode(20), nullable=False)
    payment_state_updated_at = db.Column(db.DateTime)
    payment_state_updated_by_id = db.Column(db.Uuid, db.ForeignKey('users.id'))
    payment_state_updated_by = db.relationship(User, foreign_keys=[payment_state_updated_by_id])
    cancelation_reason = db.Column(db.Unicode(200))

    def __init__(self, party, order_number, placed_by, first_names, last_name,
                 date_of_birth, zip_code, city, street):
        self.party = party
        self.order_number = order_number
        self.placed_by = placed_by
        self.first_names = first_names
        self.last_name = last_name
        self.date_of_birth = date_of_birth
        self.zip_code = zip_code
        self.city = city
        self.street = street
        self.payment_state = PaymentState.open

    @hybrid_property
    def payment_state(self):
        return PaymentState[self._payment_state]

    @payment_state.setter
    def payment_state(self, state):
        assert state is not None
        self._payment_state = state.name

    def add_item(self, article, quantity):
        """Add an article as an item to this order.

        Return the resulting order item so it can be added to the
        database session.
        """
        return OrderItem(self, article, quantity=quantity)

    def cancel(self, reason):
        """Cancel the order."""
        self._update_payment_state(PaymentState.canceled)
        self.cancelation_reason = reason

    def mark_as_paid(self):
        """Mark the order as being paid for."""
        self._update_payment_state(PaymentState.paid)

    def _update_payment_state(self, state):
        self.payment_state = state
        self.payment_state_updated_at = datetime.now()
        self.payment_state_updated_by = g.current_user

    def collect_articles(self):
        """Return the articles associated with this order."""
        return {item.article for item in self.items}

    def calculate_total_price(self):
        return sum(item.price * item.quantity for item in self.items)

    def __repr__(self):
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add('party', self.party_id) \
            .add_with_lookup('order_number') \
            .add('placed_by', self.placed_by.screen_name) \
            .add_custom('{:d} items'.format(len(self.items))) \
            .add_custom(self.payment_state.name) \
            .build()


class OrderItem(db.Model):
    """An item that belongs to an order."""
    __tablename__ = 'shop_order_items'

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    order_id = db.Column(db.Uuid, db.ForeignKey('shop_orders.id'), index=True, nullable=False)
    order = db.relationship(Order, backref='items')
    article_id = db.Column(db.Uuid, db.ForeignKey('shop_articles.id'), index=True, nullable=False)
    article = db.relationship(Article, backref='order_items')
    description = db.Column(db.Unicode(80), nullable=False)
    _price = db.Column('price', db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    def __init__(self, order, article, quantity):
        self.order = order
        self.article = article
        self.description = article.description
        self.price = article.price
        self.quantity = quantity

    @hybrid_property
    def price(self):
        return EuroAmount.from_int(self._price)

    @price.setter
    def price(self, amount):
        self._price = amount.to_int()


# -------------------------------------------------------------------- #
# sequences


PartySequencePurpose = Enum('PartySequencePurpose', ['article', 'order'])


class PartySequence(db.Model):
    """A sequence for a party and a purpose."""
    __tablename__ = 'shop_party_sequences'

    party_id = db.Column(db.Unicode(20), db.ForeignKey('parties.id'), primary_key=True)
    party = db.relationship(Party)
    _purpose = db.Column('purpose', db.Unicode(20), primary_key=True)
    value = db.Column(db.Integer, default=0, nullable=False)

    def __init__(self, party, purpose):
        self.party = party
        self.purpose = purpose

    @hybrid_property
    def purpose(self):
        return PartySequencePurpose[self._purpose]

    @purpose.setter
    def purpose(self, purpose):
        assert purpose is not None
        self._purpose = purpose.name

    def __repr__(self):
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add('party', self.party_id) \
            .add('purpose', self.purpose.name) \
            .add_with_lookup('value') \
            .build()


# -------------------------------------------------------------------- #
# shopping cart


class Cart(object):
    """A shopping cart."""

    def __init__(self):
        self.items = []

    def add_item(self, item):
        self.items.append(item)

    def is_empty(self):
        return not self.items

    def __repr__(self):
        return ReprBuilder(self) \
            .add_custom('{:d} items'.format(len(self.items))) \
            .build()


class CartItem(object):
    """An article with a quantity."""

    def __init__(self, article, quantity):
        if quantity < 1:
            raise ValueError('Quantity must be a positive number.')

        self.article = article
        self.quantity = quantity

    def __repr__(self):
        return ReprBuilder(self) \
            .add_with_lookup('item_number') \
            .add_with_lookup('quantity') \
            .build()
