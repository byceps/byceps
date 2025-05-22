"""
byceps.services.shop.catalog.catalog_domain_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import dataclasses

from byceps.services.shop.shop.models import ShopID
from byceps.util.uuid import generate_uuid7

from .models import Catalog, CatalogID, Collection, CollectionID


# catalog


def create_catalog(shop_id: ShopID, title: str) -> Catalog:
    """Create a catalog."""
    catalog_id = CatalogID(generate_uuid7())

    return Catalog(
        id=catalog_id,
        shop_id=shop_id,
        title=title,
    )


def update_catalog(catalog: Catalog, title: str) -> Catalog:
    """Update a catalog."""
    return dataclasses.replace(catalog, title=title)


# collection


def create_collection(catalog_id: CatalogID, title: str) -> Collection:
    """Create a collection."""
    collection_id = CollectionID(generate_uuid7())

    return Collection(
        id=collection_id,
        catalog_id=catalog_id,
        title=title,
        position=-1,
        product_numbers=[],
    )


def update_collection(collection: Collection, title: str) -> Collection:
    """Update a collection."""
    return dataclasses.replace(collection, title=title)
