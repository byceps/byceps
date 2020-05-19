"""
byceps.services.shop.catalog.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ....database import db
from ....util.instances import ReprBuilder

from .transfer.models import CatalogID


class Catalog(db.Model):
    """A catalog to offer articles."""

    __tablename__ = 'shop_catalogs'

    id = db.Column(db.UnicodeText, primary_key=True)
    title = db.Column(db.UnicodeText, unique=True, nullable=False)

    def __init__(self, catalog_id: CatalogID, title: str) -> None:
        self.id = catalog_id
        self.title = title

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .build()
