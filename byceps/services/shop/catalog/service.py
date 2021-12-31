"""
byceps.services.shop.catalog.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from typing import Optional

from sqlalchemy import select

from ....database import db

from ..article.transfer.models import ArticleNumber
from ..shop.transfer.models import ShopID

from .dbmodels import (
    Catalog as DbCatalog,
    CatalogArticle as DbCatalogArticle,
    Collection as DbCollection,
)
from .transfer.models import (
    Catalog,
    CatalogArticleID,
    CatalogID,
    Collection,
    CollectionID,
)


# catalog


def create_catalog(shop_id: ShopID, title: str) -> Catalog:
    """Create a catalog."""
    db_catalog = DbCatalog(shop_id, title)

    db.session.add(db_catalog)
    db.session.commit()

    return _db_entity_to_catalog(db_catalog)


def find_catalog(catalog_id: CatalogID) -> Optional[Catalog]:
    """Return the catalog with that ID, or `None` if not found."""
    db_catalog = _find_db_catalog(catalog_id)

    if db_catalog is None:
        return None

    return _db_entity_to_catalog(db_catalog)


def _find_db_catalog(catalog_id: CatalogID) -> Optional[DbCatalog]:
    """Return the catalog database entity with that ID, or `None` if not
    found.
    """
    return db.session.get(DbCatalog, catalog_id)


def get_catalogs_for_shop(shop_id: ShopID) -> list[Catalog]:
    """Return all catalogs for that shop."""
    db_catalogs = db.session.execute(
        select(DbCatalog)
        .filter_by(shop_id=shop_id)
    ).scalars().all()

    return [_db_entity_to_catalog(db_catalog) for db_catalog in db_catalogs]


def _db_entity_to_catalog(db_catalog: DbCatalog) -> Catalog:
    return Catalog(
        id=db_catalog.id,
        shop_id=db_catalog.shop_id,
        title=db_catalog.title,
    )


# collection


def create_collection(catalog_id: CatalogID, title: str) -> Collection:
    """Create a collection."""
    db_catalog = _find_db_catalog(catalog_id)
    if db_catalog is None:
        raise ValueError(f'Unknown catalog ID "{catalog_id}"')

    db_collection = DbCollection(catalog_id, title)

    db_catalog.collections.append(db_collection)
    db.session.commit()

    return _db_entity_to_collection(db_collection)


def delete_collection(collection_id: CollectionID) -> None:
    """Delete the collection."""
    db.session.query(DbCollection) \
        .filter_by(id=collection_id) \
        .delete()

    db.session.commit()


def get_collections_for_catalog(catalog_id: CatalogID) -> list[Collection]:
    """Return the catalog's collections."""
    db_collections = db.session \
        .query(DbCollection) \
        .filter_by(catalog_id=catalog_id) \
        .order_by(DbCollection.position) \
        .all()

    return [
        _db_entity_to_collection(db_collection)
        for db_collection in db_collections
    ]


def _db_entity_to_collection(db_collection: DbCollection) -> Collection:
    return Collection(
        id=db_collection.id,
        catalog_id=db_collection.catalog_id,
        title=db_collection.title,
        position=db_collection.position,
        article_numbers=[],
    )


# article assignment


def add_article_to_collection(
    article_number: ArticleNumber, collection_id: CollectionID
) -> CatalogArticleID:
    """Add article to collection."""
    db_collection = db.session.get(DbCollection, collection_id)
    if db_collection is None:
        raise ValueError(f'Unknown collection ID "{collection_id}"')

    db_catalog_article = DbCatalogArticle(collection_id, article_number)

    db_collection.catalog_articles.append(db_catalog_article)
    db.session.commit()

    return db_catalog_article.id


def remove_article_from_collection(
    catalog_article_id: CatalogArticleID,
) -> None:
    """Remove article from collection."""
    db.session.query(DbCatalogArticle) \
        .filter_by(id=catalog_article_id) \
        .delete()

    db.session.commit()
