"""
byceps.services.shop.catalog.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from typing import List, NewType
from uuid import UUID

from ...article.transfer.models import ArticleNumber


CatalogID = NewType('CatalogID', str)


CollectionID = NewType('CollectionID', UUID)


CatalogArticleID = NewType('CatalogArticleID', UUID)


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
    article_numbers: List[ArticleNumber]


@dataclass(frozen=True)
class CatalogArticle:
    id: CatalogArticleID
    collection_id: CollectionID
    article_number: ArticleNumber
    position: int
