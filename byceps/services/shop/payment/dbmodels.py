"""
byceps.services.shop.payment.dbmodels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.database import db
from byceps.services.shop.storefront.models import StorefrontID


class DbPaymentGateway(db.Model):
    """A payment gateway.

    Offers one or more payment methods.
    """

    __tablename__ = 'shop_payment_gateways'

    id = db.Column(db.UnicodeText, primary_key=True)
    name = db.Column(db.UnicodeText, unique=True)
    enabled = db.Column(db.Boolean, nullable=False)

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

    storefront_id = db.Column(
        db.UnicodeText, db.ForeignKey('shop_storefronts.id'), primary_key=True
    )
    payment_gateway_id = db.Column(
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
