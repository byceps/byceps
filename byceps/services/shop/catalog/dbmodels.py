"""
byceps.services.shop.catalog.dbmodels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import Mapped, mapped_column, relationship

from byceps.database import db, generate_uuid7
from byceps.services.shop.article.models import ArticleID
from byceps.services.shop.shop.models import ShopID
from byceps.util.instances import ReprBuilder

from .models import CatalogArticleID, CatalogID, CollectionID


class DbCatalog(db.Model):
    """A catalog to offer articles."""

    __tablename__ = 'shop_catalogs'

    id: Mapped[CatalogID] = mapped_column(
        db.Uuid, default=generate_uuid7, primary_key=True
    )
    shop_id: Mapped[ShopID] = mapped_column(
        db.UnicodeText, db.ForeignKey('shops.id'), index=True
    )
    title: Mapped[str] = mapped_column(db.UnicodeText, unique=True)

    def __init__(self, shop_id: ShopID, title: str) -> None:
        self.shop_id = shop_id
        self.title = title

    def __repr__(self) -> str:
        return ReprBuilder(self).add_with_lookup('id').build()


class DbCollection(db.Model):
    """A group of articles inside of catalog."""

    __tablename__ = 'shop_catalog_collections'
    __table_args__ = (db.UniqueConstraint('catalog_id', 'title'),)

    id: Mapped[CollectionID] = mapped_column(
        db.Uuid, default=generate_uuid7, primary_key=True
    )
    catalog_id: Mapped[CatalogID] = mapped_column(
        db.Uuid, db.ForeignKey('shop_catalogs.id'), index=True
    )
    title: Mapped[str] = mapped_column(db.UnicodeText)
    position: Mapped[int] = mapped_column(db.Integer)

    catalog: Mapped[DbCatalog] = relationship(
        DbCatalog,
        backref=db.backref(
            'collections',
            order_by=position,
            collection_class=ordering_list('position', count_from=1),
        ),
    )

    def __init__(self, catalog_id: CatalogID, title: str) -> None:
        self.catalog_id = catalog_id
        self.title = title

    def __repr__(self) -> str:
        return (
            ReprBuilder(self)
            .add_with_lookup('catalog_id')
            .add_with_lookup('title')
            .build()
        )


class DbCatalogArticle(db.Model):
    """The assignment of an article to a collection."""

    __tablename__ = 'shop_catalog_articles'
    __table_args__ = (db.UniqueConstraint('collection_id', 'article_id'),)

    id: Mapped[CatalogArticleID] = mapped_column(
        db.Uuid, default=generate_uuid7, primary_key=True
    )
    collection_id: Mapped[CollectionID] = mapped_column(
        db.Uuid,
        db.ForeignKey('shop_catalog_collections.id'),
        index=True,
        nullable=False,
    )
    article_id: Mapped[ArticleID] = mapped_column(
        db.Uuid, db.ForeignKey('shop_articles.id'), index=True
    )
    position: Mapped[int] = mapped_column(db.Integer)

    collection: Mapped[DbCollection] = relationship(
        DbCollection,
        backref=db.backref(
            'catalog_articles',
            order_by=position,
            collection_class=ordering_list('position', count_from=1),
        ),
    )

    def __init__(
        self, collection_id: CollectionID, article_id: ArticleID
    ) -> None:
        self.collection_id = collection_id
        self.article_id = article_id
