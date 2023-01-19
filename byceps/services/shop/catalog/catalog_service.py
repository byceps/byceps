"""
byceps.services.shop.catalog.catalog_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional

from sqlalchemy import delete, select

from ....database import db

from ..article.models import ArticleID
from ..shop.models import ShopID

from .dbmodels import DbCatalog, DbCatalogArticle, DbCollection
from .models import (
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


def update_catalog(catalog_id: CatalogID, title: str) -> Catalog:
    """Update a catalog."""
    db_catalog = _find_db_catalog(catalog_id)

    if db_catalog is None:
        raise ValueError(f'Unknown shop catalog ID "{catalog_id}"')

    db_catalog.title = title

    db.session.commit()

    return _db_entity_to_catalog(db_catalog)


def find_catalog(catalog_id: CatalogID) -> Optional[Catalog]:
    """Return the catalog with that ID, or `None` if not found."""
    db_catalog = _find_db_catalog(catalog_id)

    if db_catalog is None:
        return None

    return _db_entity_to_catalog(db_catalog)


def get_catalog(catalog_id: CatalogID) -> Catalog:
    """Return the catalog with that ID."""
    catalog = find_catalog(catalog_id)

    if catalog is None:
        raise ValueError(f'Unknown shop catalog ID "{catalog_id}"')

    return catalog


def _find_db_catalog(catalog_id: CatalogID) -> Optional[DbCatalog]:
    """Return the catalog database entity with that ID, or `None` if not
    found.
    """
    return db.session.get(DbCatalog, catalog_id)


def get_catalogs_for_shop(shop_id: ShopID) -> list[Catalog]:
    """Return all catalogs for that shop."""
    db_catalogs = db.session.scalars(
        select(DbCatalog).filter_by(shop_id=shop_id)
    ).all()

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


def update_collection(collection_id: CollectionID, title: str) -> Collection:
    """Update a collection."""
    db_collection = _find_db_collection(collection_id)

    if db_collection is None:
        raise ValueError(f'Unknown shop collection ID "{collection_id}"')

    db_collection.title = title

    db.session.commit()

    return _db_entity_to_collection(db_collection)


def delete_collection(collection_id: CollectionID) -> None:
    """Delete the collection."""
    db.session.execute(
        delete(DbCollection).where(DbCollection.id == collection_id)
    )
    db.session.commit()


def find_collection(collection_id: CollectionID) -> Optional[Collection]:
    """Return the collection with that ID, or `None` if not found."""
    db_collection = _find_db_collection(collection_id)

    if db_collection is None:
        return None

    return _db_entity_to_collection(db_collection)


def _find_db_collection(collection_id: CollectionID) -> Optional[DbCollection]:
    """Return the collection database entity with that ID, or `None` if
    not found.
    """
    return db.session.get(DbCollection, collection_id)


def get_collections_for_catalog(catalog_id: CatalogID) -> list[Collection]:
    """Return the catalog's collections."""
    db_collections = db.session.scalars(
        select(DbCollection)
        .filter_by(catalog_id=catalog_id)
        .order_by(DbCollection.position)
    ).all()

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
    article_id: ArticleID, collection_id: CollectionID
) -> CatalogArticleID:
    """Add article to collection."""
    db_collection = db.session.get(DbCollection, collection_id)
    if db_collection is None:
        raise ValueError(f'Unknown collection ID "{collection_id}"')

    db_catalog_article = DbCatalogArticle(collection_id, article_id)

    db_collection.catalog_articles.append(db_catalog_article)
    db.session.commit()

    return db_catalog_article.id


def remove_article_from_collection(
    catalog_article_id: CatalogArticleID,
) -> None:
    """Remove article from collection."""
    db.session.execute(
        delete(DbCatalogArticle).where(
            DbCatalogArticle.id == catalog_article_id
        )
    )
    db.session.commit()
