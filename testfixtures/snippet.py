"""
testfixtures.snippet
~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.snippet.models.snippet import \
    CurrentVersionAssociation, Snippet, SnippetVersion
from byceps.services.snippet.transfer.models import SnippetType


def create_document(party_id, name):
    return _create_snippet(party_id, name, SnippetType.document)


def create_fragment(party_id, name):
    return _create_snippet(party_id, name, SnippetType.fragment)


def _create_snippet(party_id, name, type_):
    return Snippet('party', party_id, party_id, name, type_)


def create_snippet_version(snippet, creator_id, *, created_at=None,
                           title='', head='', body='', image_url_path=None):
    version = SnippetVersion(
        snippet=snippet,
        creator_id=creator_id,
        title=title,
        head=head,
        body=body,
        image_url_path=image_url_path)

    if created_at is not None:
        version.created_at = created_at

    return version


def create_current_version_association(snippet, version):
    return CurrentVersionAssociation(
        snippet=snippet,
        version=version)
