"""
byceps.services.shop.catalog.catalog_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections import defaultdict
from datetime import datetime

from sqlalchemy import delete, select

from byceps.database import db
from byceps.services.shop.product.dbmodels.product import DbProduct
from byceps.services.shop.product import product_service
from byceps.services.shop.product.models import (
    Product,
    ProductCollection,
    ProductCollectionItem,
    ProductID,
)
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


def get_collections_for_catalog(
    catalog_id: CatalogID, *, include_unavailable_products: bool
) -> list[ProductCollection]:
    """Return the catalog's collections."""
    # Attention: Products attached to products assigned to a catalog
    # will not be included at this time!

    db_collections = db.session.scalars(
        select(DbCollection)
        .filter_by(catalog_id=catalog_id)
        .order_by(DbCollection.position)
    ).all()

    db_catalog_products = db.session.scalars(
        select(DbCatalogProduct)
        .join(DbCollection)
        .filter(DbCollection.catalog_id == catalog_id)
        .order_by(DbCatalogProduct.position)
    ).all()

    collection_ids_to_products = defaultdict(list)

    product_ids = {
        db_catalog_product.product_id
        for db_catalog_product in db_catalog_products
    }

    now = datetime.utcnow()

    products_stmt = (
        select(DbProduct)
        .filter(DbProduct.id.in_(product_ids))
        .filter_by(not_directly_orderable=False)
        .filter_by(separate_order_required=False)
    )

    if not include_unavailable_products:
        products_stmt = (
            products_stmt
            # Select only products that are available in between the
            # temporal boundaries for this product, if specified.
            .filter(
                db.or_(
                    DbProduct.available_from.is_(None),
                    now >= DbProduct.available_from,
                )
            ).filter(
                db.or_(
                    DbProduct.available_until.is_(None),
                    now < DbProduct.available_until,
                )
            )
        )

    db_products = db.session.scalars(products_stmt).all()

    products = [
        product_service._db_entity_to_product(db_product)
        for db_product in db_products
    ]

    products_indexed_by_id = {product.id: product for product in products}

    for db_catalog_product in db_catalog_products:
        collection_id = db_catalog_product.collection_id
        product_id = db_catalog_product.product_id

        product = products_indexed_by_id.get(product_id)
        if not product:
            continue

        collection_ids_to_products[collection_id].append(product)

    return [
        _db_entity_to_product_collection(
            db_collection, collection_ids_to_products[db_collection.id]
        )
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


def _db_entity_to_product_collection(
    db_collection: DbCollection, products: list[Product]
) -> ProductCollection:
    items = [
        _product_to_product_collection_item(product) for product in products
    ]

    return ProductCollection(
        title=db_collection.title,
        items=items,
    )


def _product_to_product_collection_item(
    product: Product,
) -> ProductCollectionItem:
    return ProductCollectionItem(
        product=product,
        fixed_quantity=None,
        has_fixed_quantity=False,
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
