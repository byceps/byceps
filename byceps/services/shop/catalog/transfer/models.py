"""
byceps.services.shop.catalog.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from dataclasses import dataclass
from typing import NewType
from uuid import UUID


CatalogID = NewType('CatalogID', str)


CollectionID = NewType('CollectionID', UUID)


@dataclass(frozen=True)
class Catalog:
    id: CatalogID
    title: str


@dataclass(frozen=True)
class Collection:
    id: CollectionID
    catalog_id: CatalogID
    title: str
    position: int
