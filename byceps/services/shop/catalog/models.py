"""
byceps.services.shop.catalog.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from typing import NewType
from uuid import UUID

from ..article.models import ArticleNumber
from ..shop.models import ShopID


CatalogID = NewType('CatalogID', UUID)


CollectionID = NewType('CollectionID', UUID)


CatalogArticleID = NewType('CatalogArticleID', UUID)


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
    article_numbers: list[ArticleNumber]


@dataclass(frozen=True)
class CatalogArticle:
    id: CatalogArticleID
    collection_id: CollectionID
    article_number: ArticleNumber
    position: int
