"""
byceps.services.shop.catalog.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import List, Optional

from ....database import db

from .models import Catalog as DbCatalog
from .transfer.models import Catalog, CatalogID


def create_catalog(catalog_id: CatalogID, title: str) -> Catalog:
    """Create a catalog."""
    catalog = DbCatalog(catalog_id, title)

    db.session.add(catalog)
    db.session.commit()

    return _db_entity_to_catalog(catalog)


def find_catalog(catalog_id: CatalogID) -> Optional[Catalog]:
    """Return the catalog with that id, or `None` if not found."""
    catalog = DbCatalog.query.get(catalog_id)

    if catalog is None:
        return None

    return _db_entity_to_catalog(catalog)


def get_all_catalogs() -> List[Catalog]:
    """Return all catalogs."""
    catalogs = DbCatalog.query.all()

    return [_db_entity_to_catalog(catalog) for catalog in catalogs]


def _db_entity_to_catalog(catalog: DbCatalog) -> Catalog:
    return Catalog(
        catalog.id,
        catalog.title,
    )
