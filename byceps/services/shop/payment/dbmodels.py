"""
byceps.services.shop.payment.dbmodels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from sqlalchemy.orm import Mapped, mapped_column

from byceps.database import db
from byceps.services.shop.storefront.models import StorefrontID


class DbPaymentGateway(db.Model):
    """A payment gateway.

    Offers one or more payment methods.
    """

    __tablename__ = 'shop_payment_gateways'

    id: Mapped[str] = mapped_column(db.UnicodeText, primary_key=True)
    name: Mapped[str] = mapped_column(db.UnicodeText, unique=True)
    enabled: Mapped[bool]

    def __init__(
        self,
        payment_gateway_id: str,
        name: str,
        enabled: bool,
    ) -> None:
        self.id = payment_gateway_id
        self.name = name
        self.enabled = enabled


class DbStorefrontPaymentGateway(db.Model):
    """A payment gateway enabled for a storefront."""

    __tablename__ = 'shop_storefront_payment_gateways'

    storefront_id: Mapped[StorefrontID] = mapped_column(
        db.UnicodeText, db.ForeignKey('shop_storefronts.id'), primary_key=True
    )
    payment_gateway_id: Mapped[str] = mapped_column(
        db.UnicodeText,
        db.ForeignKey('shop_payment_gateways.id'),
        primary_key=True,
    )

    def __init__(
        self,
        storefront_id: StorefrontID,
        payment_gateway_id: str,
    ) -> None:
        self.storefront_id = storefront_id
        self.payment_gateway_id = payment_gateway_id
