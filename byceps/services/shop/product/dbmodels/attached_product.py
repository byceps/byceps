"""
byceps.services.shop.product.dbmodels.attached_product
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from sqlalchemy.orm import Mapped, mapped_column, relationship

from byceps.database import db
from byceps.services.shop.product.models import ProductID, AttachedProductID

from .product import DbProduct


class DbAttachedProduct(db.Model):
    """A product that is attached to another product."""

    __tablename__ = 'shop_attached_products'
    __table_args__ = (
        db.UniqueConstraint('product_id', 'attached_to_product_id'),
    )

    id: Mapped[AttachedProductID] = mapped_column(db.Uuid, primary_key=True)
    product_id: Mapped[ProductID] = mapped_column(
        db.Uuid, db.ForeignKey('shop_products.id'), index=True
    )
    product: Mapped[DbProduct] = relationship(
        DbProduct,
        foreign_keys=[product_id],
        backref=db.backref('products_attached_to', collection_class=set),
    )
    quantity: Mapped[int] = mapped_column(db.CheckConstraint('quantity > 0'))
    attached_to_product_id: Mapped[ProductID] = mapped_column(
        db.Uuid, db.ForeignKey('shop_products.id'), index=True
    )
    attached_to_product: Mapped[DbProduct] = relationship(
        DbProduct,
        foreign_keys=[attached_to_product_id],
        backref=db.backref('attached_products', collection_class=set),
    )

    def __init__(
        self,
        attached_product_id: AttachedProductID,
        product_id: ProductID,
        quantity: int,
        attached_to_product_id: ProductID,
    ) -> None:
        self.id = attached_product_id
        self.product_id = product_id
        self.quantity = quantity
        self.attached_to_product_id = attached_to_product_id
