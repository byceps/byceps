"""
byceps.services.shop.catalog.catalog_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from sqlalchemy import delete, select

from byceps.database import db
from byceps.services.shop.product.models import ProductID
from byceps.services.shop.shop.models import ShopID
from byceps.util.uuid import generate_uuid7

from .dbmodels import DbCatalog, DbCatalogProduct, DbCollection
from .models import (
    Catalog,
    CatalogProductID,
    CatalogID,
    Collection,
    CollectionID,
)


# catalog


def create_catalog(shop_id: ShopID, title: str) -> Catalog:
    """Create a catalog."""
    catalog_id = CatalogID(generate_uuid7())

    db_catalog = DbCatalog(catalog_id, shop_id, title)

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


def find_catalog(catalog_id: CatalogID) -> Catalog | None:
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


def _find_db_catalog(catalog_id: CatalogID) -> DbCatalog | None:
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

    collection_id = CollectionID(generate_uuid7())

    db_collection = DbCollection(collection_id, catalog_id, title)

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


def find_collection(collection_id: CollectionID) -> Collection | None:
    """Return the collection with that ID, or `None` if not found."""
    db_collection = _find_db_collection(collection_id)

    if db_collection is None:
        return None

    return _db_entity_to_collection(db_collection)


def _find_db_collection(collection_id: CollectionID) -> DbCollection | None:
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
        product_numbers=[],
    )


# product assignment


def add_product_to_collection(
    product_id: ProductID, collection_id: CollectionID
) -> CatalogProductID:
    """Add product to collection."""
    db_collection = db.session.get(DbCollection, collection_id)
    if db_collection is None:
        raise ValueError(f'Unknown collection ID "{collection_id}"')

    assignment_id = CatalogProductID(generate_uuid7())

    db_catalog_product = DbCatalogProduct(
        assignment_id, collection_id, product_id
    )

    db_collection.catalog_products.append(db_catalog_product)
    db.session.commit()

    return db_catalog_product.id


def remove_product_from_collection(
    catalog_product_id: CatalogProductID,
) -> None:
    """Remove product from collection."""
    db.session.execute(
        delete(DbCatalogProduct).where(
            DbCatalogProduct.id == catalog_product_id
        )
    )
    db.session.commit()
