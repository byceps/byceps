"""
byceps.services.shop.catalog.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from typing import NewType
from uuid import UUID

from byceps.services.shop.product.models import ProductID, ProductNumber
from byceps.services.shop.shop.models import ShopID


CatalogID = NewType('CatalogID', UUID)


CollectionID = NewType('CollectionID', UUID)


CatalogProductID = NewType('CatalogProductID', UUID)


@dataclass(frozen=True)
class Catalog:
    id: CatalogID
    shop_id: ShopID
    title: str


@dataclass(frozen=True)
class Collection:
    id: CollectionID
    catalog_id: CatalogID
    title: str
    position: int
    product_numbers: list[ProductNumber]


@dataclass(frozen=True)
class CatalogProduct:
    id: CatalogProductID
    collection_id: CollectionID
    product_id: ProductID
    position: int
