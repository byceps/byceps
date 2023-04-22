"""
byceps.services.shop.storefront.dbmodels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from byceps.database import db
# Make shop catalog tables available for database creation.
from byceps.services.shop.catalog.dbmodels import DbCatalog  # noqa: F401
from byceps.services.shop.catalog.models import CatalogID
from byceps.services.shop.order.models.number import OrderNumberSequenceID
from byceps.services.shop.shop.models import ShopID
from byceps.util.instances import ReprBuilder

from .models import StorefrontID


class DbStorefront(db.Model):
    """A storefront.

    The entrypoint from a site to a shop.
    """

    __tablename__ = 'shop_storefronts'

    id = db.Column(db.UnicodeText, primary_key=True)
    shop_id = db.Column(
        db.UnicodeText, db.ForeignKey('shops.id'), index=True, nullable=False
    )
    catalog_id = db.Column(
        db.Uuid, db.ForeignKey('shop_catalogs.id'), nullable=True
    )
    order_number_sequence_id = db.Column(
        db.Uuid, db.ForeignKey('shop_order_number_sequences.id'), nullable=False
    )
    closed = db.Column(db.Boolean, nullable=False)

    def __init__(
        self,
        storefront_id: StorefrontID,
        shop_id: ShopID,
        order_number_sequence_id: OrderNumberSequenceID,
        closed: bool,
        *,
        catalog_id: CatalogID | None = None,
    ) -> None:
        self.id = storefront_id
        self.shop_id = shop_id
        self.catalog_id = catalog_id
        self.order_number_sequence_id = order_number_sequence_id
        self.closed = closed

    def __repr__(self) -> str:
        return (
            ReprBuilder(self)
            .add_with_lookup('id')
            .add_with_lookup('shop_id')
            .build()
        )
