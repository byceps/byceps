"""
byceps.services.shop.catalog.catalog_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections import defaultdict
from collections.abc import Iterable
import dataclasses

from byceps.services.shop.product import product_service
from byceps.services.shop.product.models import (
    Product,
    ProductCollection,
    ProductCollectionItem,
    ProductID,
)
from byceps.services.shop.shop.models import ShopID
from byceps.util.uuid import generate_uuid7

from . import catalog_domain_service, catalog_repository
from .dbmodels import DbCatalog, DbCatalogProduct, DbCollection
from .models import (
    Catalog,
    CatalogProduct,
    CatalogProductID,
    CatalogID,
    Collection,
    CollectionID,
)


# catalog


def create_catalog(shop_id: ShopID, title: str) -> Catalog:
    """Create a catalog."""
    catalog = catalog_domain_service.create_catalog(shop_id, title)

    catalog_repository.create_catalog(catalog)

    return catalog


def update_catalog(catalog: Catalog, title: str) -> Catalog:
    """Update a catalog."""
    updated_catalog = catalog_domain_service.update_catalog(
        catalog, title=title
    )

    catalog_repository.update_catalog(updated_catalog)

    return updated_catalog


def find_catalog(catalog_id: CatalogID) -> Catalog | None:
    """Return the catalog with that ID, or `None` if not found."""
    db_catalog = catalog_repository.find_catalog(catalog_id)

    if db_catalog is None:
        return None

    return _db_entity_to_catalog(db_catalog)


def get_catalog(catalog_id: CatalogID) -> Catalog:
    """Return the catalog with that ID."""
    catalog = find_catalog(catalog_id)

    if catalog is None:
        raise ValueError(f'Unknown shop catalog ID "{catalog_id}"')

    return catalog


def get_catalogs_for_shop(shop_id: ShopID) -> list[Catalog]:
    """Return all catalogs for that shop."""
    db_catalogs = catalog_repository.get_catalogs_for_shop(shop_id)

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
    collection = catalog_domain_service.create_collection(catalog_id, title)

    position = catalog_repository.create_collection(collection)

    return dataclasses.replace(collection, position=position)


def update_collection(collection: Collection, title: str) -> Collection:
    """Update a collection."""
    updated_collection = catalog_domain_service.update_collection(
        collection, title
    )

    catalog_repository.update_collection(updated_collection)

    return updated_collection


def delete_collection(collection_id: CollectionID) -> None:
    """Delete the collection."""
    catalog_repository.delete_collection(collection_id)


def find_collection(collection_id: CollectionID) -> Collection | None:
    """Return the collection with that ID, or `None` if not found."""
    db_collection = catalog_repository.find_collection(collection_id)

    if db_collection is None:
        return None

    return _db_entities_to_collections([db_collection])[0]


def get_collections_for_catalog(catalog_id: CatalogID) -> list[Collection]:
    """Return the catalog's collections."""
    db_collections = catalog_repository.get_collections_for_catalog(catalog_id)

    return _db_entities_to_collections(db_collections)


def get_collections_and_products_for_catalog(
    catalog_id: CatalogID,
    *,
    only_currently_available: bool,
    only_directly_orderable: bool,
    only_not_requiring_separate_order: bool,
) -> list[tuple[Collection, list[Product]]]:
    """Return the catalog's collections and their products."""
    # Attention: Products attached to products assigned to a catalog
    # will not be included at this time!

    collections = get_collections_for_catalog(catalog_id)

    catalog_products = _get_catalog_products(catalog_id)

    product_ids = {
        catalog_product.product_id for catalog_product in catalog_products
    }

    products = product_service.get_products(
        product_ids,
        only_currently_available=only_currently_available,
        only_directly_orderable=only_directly_orderable,
        only_not_requiring_separate_order=only_not_requiring_separate_order,
    )

    products_indexed_by_id = {product.id: product for product in products}

    collection_ids_to_products = defaultdict(list)

    for catalog_product in catalog_products:
        collection_id = catalog_product.collection_id
        product_id = catalog_product.product_id

        product = products_indexed_by_id.get(product_id)
        if not product:
            continue

        collection_ids_to_products[collection_id].append(product)

    return [
        (collection, collection_ids_to_products[collection.id])
        for collection in collections
    ]


def get_product_collections_for_catalog(
    catalog_id: CatalogID,
    *,
    only_currently_available: bool,
    only_directly_orderable: bool,
    only_not_requiring_separate_order: bool,
) -> list[ProductCollection]:
    """Return the catalog's collections."""
    # Attention: Products attached to products assigned to a catalog
    # will not be included at this time!

    return [
        _collection_to_product_collection(collection, products)
        for collection, products in get_collections_and_products_for_catalog(
            catalog_id,
            only_currently_available=only_currently_available,
            only_directly_orderable=only_directly_orderable,
            only_not_requiring_separate_order=only_not_requiring_separate_order,
        )
    ]


def _db_entities_to_collections(
    db_collections: Iterable[DbCollection],
) -> list[Collection]:
    collection_ids = {db_collection.id for db_collection in db_collections}

    product_ids_by_collection_id = (
        catalog_repository.get_product_numbers_for_collections(collection_ids)
    )

    return [
        _db_entity_to_collection(
            db_collection,
            product_ids_by_collection_id.get(db_collection.id, set()),
        )
        for db_collection in db_collections
    ]


def _db_entity_to_collection(
    db_collection: DbCollection, product_ids: set[ProductID]
) -> Collection:
    return Collection(
        id=db_collection.id,
        catalog_id=db_collection.catalog_id,
        title=db_collection.title,
        position=db_collection.position,
        product_ids=set(product_ids),
    )


def _collection_to_product_collection(
    collection: Collection, products: list[Product]
) -> ProductCollection:
    items = [
        _product_to_product_collection_item(product) for product in products
    ]

    return ProductCollection(
        title=collection.title,
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
    assignment_id = CatalogProductID(generate_uuid7())

    catalog_repository.add_product_to_collection(
        product_id, collection_id, assignment_id
    )

    return assignment_id


def remove_product_from_collection(
    product_id: ProductID, collection_id: CollectionID
) -> None:
    """Remove product from collection."""
    catalog_repository.remove_product_from_collection(product_id, collection_id)


def _get_catalog_products(catalog_id: CatalogID) -> list[CatalogProduct]:
    """Return the catalog's catalog products."""
    db_catalog_products = catalog_repository.get_catalog_products(catalog_id)

    return [
        _db_entity_to_catalog_product(db_catalog_product)
        for db_catalog_product in db_catalog_products
    ]


def _db_entity_to_catalog_product(
    db_catalog_product: DbCatalogProduct,
) -> CatalogProduct:
    return CatalogProduct(
        id=db_catalog_product.id,
        collection_id=db_catalog_product.collection_id,
        product_id=db_catalog_product.product_id,
        position=db_catalog_product.position,
    )
