"""
byceps.blueprints.admin.snippet.helpers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional
from flask import abort

from ....services.brand import service as brand_service
from ....services.brand.transfer.models import Brand
from ....services.site import service as site_service
from ....services.site.transfer.models import Site, SiteID
from ....services.snippet.dbmodels.snippet import (
    Snippet as DbSnippet,
    SnippetVersion as DbSnippetVersion,
)
from ....services.snippet import mountpoint_service, service as snippet_service
from ....services.snippet.transfer.models import (
    Scope,
    SnippetID,
    SnippetVersionID,
)
from ....typing import BrandID


def find_brand_for_scope(scope: Scope) -> Optional[Brand]:
    if scope.type_ != 'brand':
        return None

    return brand_service.find_brand(BrandID(scope.name))


def find_site_for_scope(scope: Scope) -> Optional[Site]:
    if scope.type_ != 'site':
        return None

    return site_service.find_site(SiteID(scope.name))


def find_site_by_id(site_id: SiteID) -> Site:
    site = site_service.find_site(site_id)

    if site is None:
        abort(404)

    return site


def find_snippet_by_id(snippet_id: SnippetID) -> DbSnippet:
    snippet = snippet_service.find_snippet(snippet_id)

    if snippet is None:
        abort(404)

    return snippet


def find_snippet_version(version_id: SnippetVersionID) -> DbSnippetVersion:
    version = snippet_service.find_snippet_version(version_id)

    if version is None:
        abort(404)

    return version
