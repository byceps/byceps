"""
byceps.services.shop.order.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from collections import namedtuple
from datetime import datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy.ext.hybrid import hybrid_property

from ....database import BaseQuery, db, generate_uuid
from ....util.instances import ReprBuilder

from ...user.models.user import User

from ..article.models import Article


class Orderer(object):
    """Someone who orders articles."""

    def __init__(self, user, first_names, last_name, date_of_birth, country,
                 zip_code, city, street):
        self.user = user
        self.first_names = first_names
        self.last_name = last_name
        self.date_of_birth = date_of_birth
        self.country = country
        self.zip_code = zip_code
        self.city = city
        self.street = street


PaymentMethod = Enum('PaymentMethod', ['bank_transfer', 'cash', 'direct_debit'])


PaymentState = Enum('PaymentState', ['open', 'canceled', 'paid'])


class OrderQuery(BaseQuery):

    def for_party_id(self, party_id):
        return self.filter_by(party_id=party_id)

    def placed_by_id(self, user_id):
        return self.filter_by(placed_by_id=user_id)


class Order(db.Model):
    """An order for articles, placed by a user."""
    __tablename__ = 'shop_orders'
    query_class = OrderQuery
    __table_args__ = (
        db.UniqueConstraint('party_id', 'order_number'),
    )

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    party_id = db.Column(db.Unicode(40), db.ForeignKey('parties.id'), index=True, nullable=False)
    order_number = db.Column(db.Unicode(13), unique=True, nullable=False)
    placed_by_id = db.Column(db.Uuid, db.ForeignKey('users.id'), index=True, nullable=False)
    placed_by = db.relationship(User, foreign_keys=[placed_by_id])
    first_names = db.Column(db.Unicode(40), nullable=False)
    last_name = db.Column(db.Unicode(40), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    country = db.Column(db.Unicode(60), nullable=False)
    zip_code = db.Column(db.Unicode(5), nullable=False)
    city = db.Column(db.Unicode(40), nullable=False)
    street = db.Column(db.Unicode(40), nullable=False)
    invoice_created_at = db.Column(db.DateTime, nullable=True)
    _payment_method = db.Column('payment_method', db.Unicode(20), nullable=False)
    _payment_state = db.Column('payment_state', db.Unicode(20), nullable=False)
    payment_state_updated_at = db.Column(db.DateTime, nullable=True)
    payment_state_updated_by_id = db.Column(db.Uuid, db.ForeignKey('users.id'), nullable=True)
    payment_state_updated_by = db.relationship(User, foreign_keys=[payment_state_updated_by_id])
    cancelation_reason = db.Column(db.Unicode(200), nullable=True)
    shipping_required = db.Column(db.Boolean, nullable=False)
    shipped_at = db.Column(db.DateTime, nullable=True)

    def __init__(self, party_id, order_number, placed_by, first_names,
                 last_name, date_of_birth, country, zip_code, city, street,
                 payment_method):
        self.party_id = party_id
        self.order_number = order_number
        self.placed_by = placed_by
        self.first_names = first_names
        self.last_name = last_name
        self.date_of_birth = date_of_birth
        self.country = country
        self.zip_code = zip_code
        self.city = city
        self.street = street
        self.payment_method = payment_method
        self.payment_state = PaymentState.open

    @hybrid_property
    def payment_method(self):
        return PaymentMethod[self._payment_method]

    @payment_method.setter
    def payment_method(self, method):
        assert method is not None
        self._payment_method = method.name

    @hybrid_property
    def payment_state(self):
        return PaymentState[self._payment_state]

    @payment_state.setter
    def payment_state(self, state):
        assert state is not None
        self._payment_state = state.name

    @property
    def is_open(self):
        return self.payment_state == PaymentState.open

    @property
    def is_canceled(self):
        return self.payment_state == PaymentState.canceled

    @property
    def is_paid(self):
        return self.payment_state == PaymentState.paid

    @property
    def item_total_quantity(self):
        """Return the sum of all items' quantities."""
        return sum(item.quantity for item in self.items)

    def collect_articles(self):
        """Return the articles associated with this order."""
        return {item.article for item in self.items}

    def calculate_total_price(self):
        return Decimal(sum(item.price * item.quantity for item in self.items))

    @property
    def is_invoiced(self):
        return self.invoice_created_at is not None

    @property
    def is_shipping_required(self):
        return self.shipping_required

    @property
    def is_shipped(self):
        return self.shipped_at is not None

    def to_tuple(self):
        """Return a tuple representation of (parts of) this entity."""
        items = [item.to_tuple() for item in self.items]

        return OrderTuple(
            self.id,
            self.party_id,
            self.order_number,
            self.created_at,
            self.placed_by_id,
            self.first_names,
            self.last_name,
            self.date_of_birth,
            self.country,
            self.zip_code,
            self.city,
            self.street,
            self.payment_method,
            self.payment_state,
            self.is_open,
            self.is_canceled,
            self.is_paid,
            self.is_invoiced,
            self.is_shipping_required,
            self.is_shipped,
            self.cancelation_reason,
            items,
            self.item_total_quantity,
            self.calculate_total_price(),
        )

    def __repr__(self):
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add('party', self.party_id) \
            .add_with_lookup('order_number') \
            .add('placed_by', self.placed_by.screen_name) \
            .add_custom('{:d} items'.format(len(self.items))) \
            .add_custom(self.payment_state.name) \
            .build()


OrderTuple = namedtuple('OrderTuple', [
    'id',
    'party_id',
    'order_number',
    'created_at',
    'placed_by_id',
    'first_names',
    'last_name',
    'date_of_birth',
    'country',
    'zip_code',
    'city',
    'street',
    'payment_method',
    'payment_state',
    'is_open',
    'is_canceled',
    'is_paid',
    'is_invoiced',
    'is_shipping_required',
    'is_shipped',
    'cancelation_reason',
    'items',
    'total_item_quantity',
    'total_price',
])


class OrderItem(db.Model):
    """An item that belongs to an order."""
    __tablename__ = 'shop_order_items'

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    order_number = db.Column(db.Unicode(13), db.ForeignKey('shop_orders.order_number'), index=True, nullable=False)
    order = db.relationship(Order, backref='items')
    article_number = db.Column(db.Unicode(20), db.ForeignKey('shop_articles.item_number'), index=True, nullable=False)
    article = db.relationship(Article, backref='order_items')
    description = db.Column(db.Unicode(80), nullable=False)
    price = db.Column(db.Numeric(6, 2), nullable=False)
    tax_rate = db.Column(db.Numeric(3, 3), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    shipping_required = db.Column(db.Boolean, nullable=False)

    def __init__(self, order, article, quantity):
        self.order = order
        self.article = article
        self.description = article.description
        self.price = article.price
        self.tax_rate = article.tax_rate
        self.quantity = quantity
        self.shipping_required = article.shipping_required

    @property
    def unit_price(self):
        return self.price

    @property
    def line_price(self):
        return self.unit_price * self.quantity

    def to_tuple(self):
        """Return a tuple representation of (parts of) this entity."""
        return OrderItemTuple(
            self.article_number,
            self.description,
            self.unit_price,
            self.tax_rate,
            self.quantity,
            self.line_price,
        )


OrderItemTuple = namedtuple('OrderItemTuple',
    'article_number, description, unit_price, tax_rate, quantity, line_price')


class OrderEvent(db.Model):
    """An event that refers to an order."""
    __tablename__ = 'shop_order_events'

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    occured_at = db.Column(db.DateTime, nullable=False)
    event_type = db.Column(db.Unicode(40), index=True, nullable=False)
    order_id = db.Column(db.Uuid, db.ForeignKey('shop_orders.id'), index=True, nullable=False)
    data = db.Column(db.JSONB)

    def __init__(self, occured_at, event_type, order_id, **data):
        self.occured_at = occured_at
        self.event_type = event_type
        self.order_id = order_id
        self.data = data

    def __repr__(self):
        return ReprBuilder(self) \
            .add_custom(repr(self.event_type)) \
            .add_with_lookup('order_id') \
            .add_with_lookup('data') \
            .build()
