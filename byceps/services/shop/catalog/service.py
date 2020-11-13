"""
byceps.services.shop.catalog.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import List, Optional

from ....database import db

from ..article.transfer.models import ArticleNumber

from .models import (
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


def create_catalog(catalog_id: CatalogID, title: str) -> Catalog:
    """Create a catalog."""
    catalog = DbCatalog(catalog_id, title)

    db.session.add(catalog)
    db.session.commit()

    return _db_entity_to_catalog(catalog)


def find_catalog(catalog_id: CatalogID) -> Optional[Catalog]:
    """Return the catalog with that ID, or `None` if not found."""
    catalog = _find_db_catalog(catalog_id)

    if catalog is None:
        return None

    return _db_entity_to_catalog(catalog)


def _find_db_catalog(catalog_id: CatalogID) -> Optional[DbCatalog]:
    """Return the catalog database entity with that ID, or `None` if not
    found.
    """
    return DbCatalog.query.get(catalog_id)


def get_all_catalogs() -> List[Catalog]:
    """Return all catalogs."""
    catalogs = DbCatalog.query.all()

    return [_db_entity_to_catalog(catalog) for catalog in catalogs]


def _db_entity_to_catalog(catalog: DbCatalog) -> Catalog:
    return Catalog(
        catalog.id,
        catalog.title,
    )


# collection


def create_collection(catalog_id: CatalogID, title: str) -> Collection:
    """Create a collection."""
    catalog = _find_db_catalog(catalog_id)
    if catalog is None:
        raise ValueError(f'Unknown catalog ID "{catalog_id}"')

    collection = DbCollection(catalog_id, title)

    catalog.collections.append(collection)
    db.session.commit()

    return _db_entity_to_collection(collection)


def delete_collection(collection_id: CollectionID) -> None:
    """Delete the collection."""
    db.session.query(DbCollection) \
        .filter_by(id=collection_id) \
        .delete()

    db.session.commit()


def get_collections_for_catalog(catalog_id: CatalogID) -> List[Collection]:
    """Return the catalog's collections."""
    collections = DbCollection.query \
        .filter_by(catalog_id=catalog_id) \
        .order_by(DbCollection.position) \
        .all()

    return [_db_entity_to_collection(collection) for collection in collections]


def _db_entity_to_collection(collection: DbCollection) -> Collection:
    return Collection(
        collection.id,
        collection.catalog_id,
        collection.title,
        collection.position,
        [],
    )


# article assignment


def add_article_to_collection(
    article_number: ArticleNumber, collection_id: CollectionID
) -> CatalogArticleID:
    """Add article to collection."""
    collection = DbCollection.query.get(collection_id)
    if collection is None:
        raise ValueError(f'Unknown collection ID "{collection_id}"')

    catalog_article = DbCatalogArticle(collection_id, article_number)

    collection.catalog_articles.append(catalog_article)
    db.session.commit()

    return catalog_article.id


def remove_article_from_collection(
    catalog_article_id: CatalogArticleID,
) -> None:
    """Remove article from collection."""
    db.session.query(DbCatalogArticle) \
        .filter_by(id=catalog_article_id) \
        .delete()

    db.session.commit()
