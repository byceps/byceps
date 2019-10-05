"""
testfixtures.snippet
~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.snippet.models.snippet import (
    CurrentVersionAssociation,
    Snippet,
    SnippetVersion,
)
from byceps.services.snippet.transfer.models import Scope, SnippetType


def create_document(scope, name):
    return _create_snippet(scope, name, SnippetType.document)


def create_fragment(scope, name):
    return _create_snippet(scope, name, SnippetType.fragment)


def _create_snippet(scope, name, type_):
    return Snippet(scope, name, type_)


def create_snippet_version(
    snippet,
    creator_id,
    *,
    created_at=None,
    title='',
    head='',
    body='',
    image_url_path=None,
):
    version = SnippetVersion(
        snippet=snippet,
        creator_id=creator_id,
        title=title,
        head=head,
        body=body,
        image_url_path=image_url_path,
    )

    if created_at is not None:
        version.created_at = created_at

    return version


def create_current_version_association(snippet, version):
    return CurrentVersionAssociation(snippet=snippet, version=version)
