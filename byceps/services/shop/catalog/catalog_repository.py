"""
byceps.services.shop.catalog.catalog_repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections import defaultdict
from collections.abc import Sequence

from sqlalchemy import delete, select

from byceps.database import db
from byceps.services.shop.product.dbmodels.product import DbProduct
from byceps.services.shop.product.models import ProductID
from byceps.services.shop.shop.models import ShopID

from .dbmodels import DbCatalog, DbCatalogProduct, DbCollection
from .models import (
    Catalog,
    CatalogProductID,
    CatalogID,
    Collection,
    CollectionID,
)


# catalog


def create_catalog(catalog: Catalog) -> None:
    """Create a catalog."""
    db_catalog = DbCatalog(catalog.id, catalog.shop_id, catalog.title)

    db.session.add(db_catalog)
    db.session.commit()


def update_catalog(catalog: Catalog) -> None:
    """Update a catalog."""
    db_catalog = get_catalog(catalog.id)

    db_catalog.title = catalog.title

    db.session.commit()


def find_catalog(catalog_id: CatalogID) -> DbCatalog | None:
    """Return the catalog with that ID, or `None` if not found."""
    return db.session.get(DbCatalog, catalog_id)


def get_catalog(catalog_id: CatalogID) -> DbCatalog:
    """Return the catalog with that ID."""
    db_catalog = find_catalog(catalog_id)

    if db_catalog is None:
        raise ValueError(f'Unknown catalog ID "{catalog_id}"')

    return db_catalog


def get_catalogs_for_shop(shop_id: ShopID) -> Sequence[DbCatalog]:
    """Return all catalogs for that shop."""
    return db.session.scalars(
        select(DbCatalog).filter_by(shop_id=shop_id)
    ).all()


# collection


def create_collection(collection: Collection) -> int:
    """Create a collection."""
    db_catalog = get_catalog(collection.catalog_id)

    db_collection = DbCollection(
        collection.id, collection.catalog_id, collection.title
    )

    db_catalog.collections.append(db_collection)
    db.session.commit()

    return collection.position


def update_collection(collection: Collection) -> None:
    """Update a collection."""
    db_collection = get_collection(collection.id)

    db_collection.title = collection.title

    db.session.commit()


def delete_collection(collection_id: CollectionID) -> None:
    """Delete the collection."""
    db.session.execute(
        delete(DbCollection).where(DbCollection.id == collection_id)
    )
    db.session.commit()


def find_collection(collection_id: CollectionID) -> DbCollection | None:
    """Return the collection with that ID, or `None` if not found."""
    return db.session.get(DbCollection, collection_id)


def get_collection(collection_id: CollectionID) -> DbCollection:
    """Return the collection with that ID."""
    db_collection = find_collection(collection_id)

    if db_collection is None:
        raise ValueError(f'Unknown collection ID "{collection_id}"')

    return db_collection


def get_collections_for_catalog(
    catalog_id: CatalogID,
) -> Sequence[DbCollection]:
    """Return the catalog's collections."""
    return db.session.scalars(
        select(DbCollection)
        .filter_by(catalog_id=catalog_id)
        .order_by(DbCollection.position)  # TODO
    ).all()


# product assignment


def add_product_to_collection(
    product_id: ProductID,
    collection_id: CollectionID,
    assignment_id: CatalogProductID,
) -> None:
    """Add product to collection."""
    db_collection = get_collection(collection_id)

    db_catalog_product = DbCatalogProduct(
        assignment_id, collection_id, product_id
    )

    db_collection.catalog_products.append(db_catalog_product)
    db.session.commit()


def remove_product_from_collection(
    product_id: ProductID,
    collection_id: CollectionID,
) -> None:
    """Remove product from collection."""
    db.session.execute(
        delete(DbCatalogProduct)
        .filter_by(collection_id=collection_id)
        .filter_by(product_id=product_id)
    )
    db.session.commit()


def get_catalog_products(catalog_id: CatalogID) -> Sequence[DbProduct]:
    """Return the products in the catalog's collections."""
    # Attention: Products attached to products assigned to a catalog
    # will not be included at this time!

    return db.session.scalars(
        select(DbCatalogProduct)
        .join(DbCollection)
        .filter(DbCollection.catalog_id == catalog_id)
        .order_by(DbCatalogProduct.position)
    ).all()


def get_product_numbers_for_collections(
    collection_ids: set[CollectionID],
) -> dict[CollectionID, set[ProductID]]:
    """Return a mapping of the IDs of collections to the IDs of the
    products in each.
    """
    rows = db.session.execute(
        select(
            DbCatalogProduct.collection_id, DbCatalogProduct.product_id
        ).filter(DbCatalogProduct.collection_id.in_(collection_ids))
    ).all()

    product_ids_by_collection_id = defaultdict(set)

    for collection_id, product_id in rows:
        product_ids_by_collection_id[collection_id].add(product_id)

    return dict(product_ids_by_collection_id)
