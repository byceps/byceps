"""
byceps.services.shop.catalog.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from dataclasses import dataclass
from typing import NewType


CatalogID = NewType('CatalogID', str)


@dataclass(frozen=True)
class Catalog:
    id: CatalogID
    title: str
