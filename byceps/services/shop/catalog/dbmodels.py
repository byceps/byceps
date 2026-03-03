"""
byceps.services.shop.catalog.dbmodels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import Mapped, mapped_column, relationship

from byceps.database import db
from byceps.services.shop.product.models import ProductID
from byceps.services.shop.shop.models import ShopID

from .models import CatalogProductID, CatalogID, CollectionID


class DbCatalog(db.Model):
    """A catalog to offer products."""

    __tablename__ = 'shop_catalogs'

    id: Mapped[CatalogID] = mapped_column(db.Uuid, primary_key=True)
    shop_id: Mapped[ShopID] = mapped_column(
        db.UnicodeText, db.ForeignKey('shops.id'), index=True
    )
    title: Mapped[str] = mapped_column(db.UnicodeText, unique=True)

    def __init__(
        self, catalog_id: CatalogID, shop_id: ShopID, title: str
    ) -> None:
        self.id = catalog_id
        self.shop_id = shop_id
        self.title = title


class DbCollection(db.Model):
    """A group of products inside of catalog."""

    __tablename__ = 'shop_catalog_collections'
    __table_args__ = (db.UniqueConstraint('catalog_id', 'title'),)

    id: Mapped[CollectionID] = mapped_column(db.Uuid, primary_key=True)
    catalog_id: Mapped[CatalogID] = mapped_column(
        db.Uuid, db.ForeignKey('shop_catalogs.id'), index=True
    )
    title: Mapped[str] = mapped_column(db.UnicodeText)
    position: Mapped[int] = mapped_column(db.Integer)

    catalog: Mapped[DbCatalog] = relationship(
        backref=db.backref(
            'collections',
            order_by=position,
            collection_class=ordering_list('position', count_from=1),
        ),
    )

    def __init__(
        self, collection_id: CollectionID, catalog_id: CatalogID, title: str
    ) -> None:
        self.id = collection_id
        self.catalog_id = catalog_id
        self.title = title


class DbCatalogProduct(db.Model):
    """The assignment of a product to a collection."""

    __tablename__ = 'shop_catalog_products'
    __table_args__ = (db.UniqueConstraint('collection_id', 'product_id'),)

    id: Mapped[CatalogProductID] = mapped_column(db.Uuid, primary_key=True)
    collection_id: Mapped[CollectionID] = mapped_column(
        db.Uuid,
        db.ForeignKey('shop_catalog_collections.id'),
        index=True,
        nullable=False,
    )
    product_id: Mapped[ProductID] = mapped_column(
        db.Uuid, db.ForeignKey('shop_products.id'), index=True
    )
    position: Mapped[int] = mapped_column(db.Integer)

    collection: Mapped[DbCollection] = relationship(
        backref=db.backref(
            'catalog_products',
            order_by=position,
            collection_class=ordering_list('position', count_from=1),
        ),
    )

    def __init__(
        self,
        assignment_id: CatalogProductID,
        collection_id: CollectionID,
        product_id: ProductID,
    ) -> None:
        self.id = assignment_id
        self.collection_id = collection_id
        self.product_id = product_id
