"""
byceps.services.shop.catalog.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from sqlalchemy.ext.orderinglist import ordering_list

from ....database import db, generate_uuid
from ....util.instances import ReprBuilder

from ..article.transfer.models import ArticleNumber

from .transfer.models import CatalogID, CollectionID


class Catalog(db.Model):
    """A catalog to offer articles."""

    __tablename__ = 'shop_catalogs'

    id = db.Column(db.UnicodeText, primary_key=True)
    title = db.Column(db.UnicodeText, unique=True, nullable=False)

    def __init__(self, catalog_id: CatalogID, title: str) -> None:
        self.id = catalog_id
        self.title = title

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .build()


class Collection(db.Model):
    """A group of articles inside of catalog."""

    __tablename__ = 'shop_catalog_collections'
    __table_args__ = (
        db.UniqueConstraint('catalog_id', 'title'),
    )

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    catalog_id = db.Column(db.UnicodeText, db.ForeignKey('shop_catalogs.id'), index=True, nullable=False)
    title = db.Column(db.UnicodeText, nullable=False)
    position = db.Column(db.Integer, nullable=False)

    catalog = db.relationship(
        Catalog,
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
        return ReprBuilder(self) \
            .add_with_lookup('catalog_id') \
            .add_with_lookup('title') \
            .build()


class CatalogArticle(db.Model):
    """The assignment of an article to a collection."""

    __tablename__ = 'shop_catalog_articles'
    __table_args__ = (
        db.UniqueConstraint('collection_id', 'article_number'),
    )

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    collection_id = db.Column(db.Uuid, db.ForeignKey('shop_catalog_collections.id'), index=True, nullable=False)
    article_number = db.Column(db.UnicodeText, db.ForeignKey('shop_articles.item_number'), index=True, nullable=False)
    position = db.Column(db.Integer, nullable=False)

    collection = db.relationship(
        Collection,
        backref=db.backref(
            'catalog_articles',
            order_by=position,
            collection_class=ordering_list('position', count_from=1),
        ),
    )

    def __init__(
        self, collection_id: CollectionID, article_number: ArticleNumber
    ) -> None:
        self.collection_id = collection_id
        self.article_number = article_number
