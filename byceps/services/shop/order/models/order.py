"""
byceps.services.shop.order.models.order
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from typing import Optional, Set

from sqlalchemy.ext.hybrid import hybrid_property

from .....database import BaseQuery, db, generate_uuid
from .....typing import UserID
from .....util.instances import ReprBuilder

from ....user.models.user import User

from ...article.models.article import Article
from ...shop.transfer.models import ShopID

from ..transfer.models import (
    Address,
    Order as OrderTransferObject,
    OrderNumber,
    PaymentMethod,
    PaymentState,
)


class OrderQuery(BaseQuery):

    def for_shop(self, shop_id: ShopID) -> BaseQuery:
        return self.filter_by(shop_id=shop_id)

    def placed_by(self, user_id: UserID) -> BaseQuery:
        return self.filter_by(placed_by_id=user_id)


class Order(db.Model):
    """An order for articles, placed by a user."""
    __tablename__ = 'shop_orders'
    query_class = OrderQuery

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False)
    shop_id = db.Column(db.UnicodeText, db.ForeignKey('shops.id'), index=True, nullable=False)
    order_number = db.Column(db.UnicodeText, unique=True, nullable=False)
    placed_by_id = db.Column(db.Uuid, db.ForeignKey('users.id'), index=True, nullable=False)
    placed_by = db.relationship(User, foreign_keys=[placed_by_id])
    first_names = db.Column(db.UnicodeText, nullable=False)
    last_name = db.Column(db.UnicodeText, nullable=False)
    country = db.Column(db.UnicodeText, nullable=False)
    zip_code = db.Column(db.UnicodeText, nullable=False)
    city = db.Column(db.UnicodeText, nullable=False)
    street = db.Column(db.UnicodeText, nullable=False)
    total_amount = db.Column(db.Numeric(7, 2), nullable=False)
    invoice_created_at = db.Column(db.DateTime, nullable=True)
    _payment_method = db.Column('payment_method', db.UnicodeText, nullable=False)
    _payment_state = db.Column('payment_state', db.UnicodeText, index=True, nullable=False)
    payment_state_updated_at = db.Column(db.DateTime, nullable=True)
    payment_state_updated_by_id = db.Column(db.Uuid, db.ForeignKey('users.id'), nullable=True)
    payment_state_updated_by = db.relationship(User, foreign_keys=[payment_state_updated_by_id])
    cancelation_reason = db.Column(db.UnicodeText, nullable=True)
    shipping_required = db.Column(db.Boolean, nullable=False)
    shipped_at = db.Column(db.DateTime, nullable=True)

    def __init__(
        self,
        shop_id: ShopID,
        order_number: OrderNumber,
        placed_by_id: UserID,
        first_names: str,
        last_name: str,
        country: str,
        zip_code: str,
        city: str,
        street,
        payment_method: PaymentMethod,
        *,
        created_at: Optional[datetime] = None,
    ) -> None:
        if created_at is None:
            created_at = datetime.utcnow()
        self.created_at = created_at
        self.shop_id = shop_id
        self.order_number = order_number
        self.placed_by_id = placed_by_id
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

    def collect_articles(self) -> Set[Article]:
        """Return the articles associated with this order."""
        return {item.article for item in self.items}

    @property
    def is_invoiced(self) -> bool:
        return self.invoice_created_at is not None

    @property
    def is_shipping_required(self) -> bool:
        return self.shipping_required

    @property
    def is_shipped(self) -> bool:
        return self.shipped_at is not None

    def to_transfer_object(self) -> OrderTransferObject:
        address = Address(
            self.country,
            self.zip_code,
            self.city,
            self.street,
        )

        items = [item.to_transfer_object() for item in self.items]

        return OrderTransferObject(
            self.id,
            self.shop_id,
            self.order_number,
            self.created_at,
            self.placed_by_id,
            self.first_names,
            self.last_name,
            address,
            self.total_amount,
            items,
            self.payment_method,
            self.payment_state,
            self.is_open,
            self.is_canceled,
            self.is_paid,
            self.is_invoiced,
            self.is_shipping_required,
            self.is_shipped,
            self.cancelation_reason,
        )

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add('shop', self.shop_id) \
            .add_with_lookup('order_number') \
            .add('placed_by', self.placed_by.screen_name) \
            .add_custom('{:d} items'.format(len(self.items))) \
            .add_custom(self.payment_state.name) \
            .build()
