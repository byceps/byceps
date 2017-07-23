"""
byceps.services.shop.order.models.order.order
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from collections import namedtuple
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import NewType, Set
from uuid import UUID

from sqlalchemy.ext.hybrid import hybrid_property

from .....database import BaseQuery, db, generate_uuid
from .....typing import PartyID, UserID
from .....util.instances import ReprBuilder

from ....user.models.user import User

from ...article.models.article import Article


OrderID = NewType('OrderID', UUID)


OrderNumber = NewType('OrderNumber', str)


class Orderer:
    """Someone who orders articles."""

    def __init__(self, user: User, first_names: str, last_name: str,
                 country: str, zip_code: str, city: str, street: str) -> None:
        self.user = user
        self.first_names = first_names
        self.last_name = last_name
        self.country = country
        self.zip_code = zip_code
        self.city = city
        self.street = street


PaymentMethod = Enum('PaymentMethod', ['bank_transfer', 'cash', 'direct_debit'])


PaymentState = Enum('PaymentState', [
    'open',
    'canceled_before_paid',
    'paid',
    'canceled_after_paid',
])


OrderTuple = namedtuple('OrderTuple', [
    'id',
    'party_id',
    'order_number',
    'created_at',
    'placed_by_id',
    'first_names',
    'last_name',
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


class OrderQuery(BaseQuery):

    def for_party_id(self, party_id: PartyID) -> BaseQuery:
        return self.filter_by(party_id=party_id)

    def placed_by_id(self, user_id: UserID) -> BaseQuery:
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

    def __init__(self, party_id: PartyID, order_number: OrderNumber,
                 placed_by: UserID, first_names: str, last_name: str,
                 country: str, zip_code: str, city: str, street,
                 payment_method: PaymentMethod) -> None:
        self.party_id = party_id
        self.order_number = order_number
        self.placed_by = placed_by
        self.first_names = first_names
        self.last_name = last_name
        self.country = country
        self.zip_code = zip_code
        self.city = city
        self.street = street
        self.payment_method = payment_method
        self.payment_state = PaymentState.open

    @hybrid_property
    def payment_method(self) -> PaymentMethod:
        return PaymentMethod[self._payment_method]

    @payment_method.setter
    def payment_method(self, method: PaymentMethod) -> None:
        assert method is not None
        self._payment_method = method.name

    @hybrid_property
    def payment_state(self) -> PaymentState:
        return PaymentState[self._payment_state]

    @payment_state.setter
    def payment_state(self, state: PaymentState) -> None:
        assert state is not None
        self._payment_state = state.name

    @property
    def is_open(self) -> bool:
        return self.payment_state == PaymentState.open

    @property
    def is_canceled(self) -> bool:
        return self.payment_state in {
            PaymentState.canceled_before_paid,
            PaymentState.canceled_after_paid,
        }

    @property
    def is_paid(self) -> bool:
        return self.payment_state == PaymentState.paid

    @property
    def item_total_quantity(self) -> int:
        """Return the sum of all items' quantities."""
        return sum(item.quantity for item in self.items)

    def collect_articles(self) -> Set[Article]:
        """Return the articles associated with this order."""
        return {item.article for item in self.items}

    def calculate_total_price(self) -> Decimal:
        return Decimal(sum(item.price * item.quantity for item in self.items))

    @property
    def is_invoiced(self) -> bool:
        return self.invoice_created_at is not None

    @property
    def is_shipping_required(self) -> bool:
        return self.shipping_required

    @property
    def is_shipped(self) -> bool:
        return self.shipped_at is not None

    def to_tuple(self) -> OrderTuple:
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

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add('party', self.party_id) \
            .add_with_lookup('order_number') \
            .add('placed_by', self.placed_by.screen_name) \
            .add_custom('{:d} items'.format(len(self.items))) \
            .add_custom(self.payment_state.name) \
            .build()
