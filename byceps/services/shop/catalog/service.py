"""
byceps.services.shop.catalog.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import List, Optional

from ....database import db

from .models import Catalog as DbCatalog, Collection as DbCollection
from .transfer.models import Catalog, CatalogID, Collection, CollectionID


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
    rows = DbCollection.query \
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
