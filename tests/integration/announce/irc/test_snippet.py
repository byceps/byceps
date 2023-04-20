"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.announce.connections import build_announcement_request
from byceps.services.snippet import snippet_service
from byceps.services.snippet.models import SnippetScope

from .helpers import build_announcement_request_for_irc


def test_announce_snippet_created(
    admin_app, created_version_and_event, webhook_for_irc
):
    expected_text = (
        'Dr.Schnipsel hat das Snippet "team_intro" '
        'im Scope "site/acme-2019-website" angelegt.'
    )
    expected = build_announcement_request_for_irc(expected_text)

    _, event = created_version_and_event

    assert build_announcement_request(event, webhook_for_irc) == expected


def test_announce_snippet_updated(
    admin_app, updated_version_and_event, webhook_for_irc
):
    expected_text = (
        'Dr.Schnipsel hat das Snippet "team_intro" '
        'im Scope "site/acme-2019-website" aktualisiert.'
    )
    expected = build_announcement_request_for_irc(expected_text)

    _, event = updated_version_and_event

    assert build_announcement_request(event, webhook_for_irc) == expected


def test_announce_snippet_deleted(
    admin_app, scope: SnippetScope, editor, webhook_for_irc
):
    expected_text = (
        'Dr.Schnipsel hat das Snippet "outdated_info" '
        'im Scope "site/acme-2019-website" gelöscht.'
    )
    expected = build_announcement_request_for_irc(expected_text)

    version, _ = snippet_service.create_snippet(
        scope, 'outdated_info', 'en', editor.id, 'This is old news. :('
    )

    success, event = snippet_service.delete_snippet(
        version.snippet_id, initiator_id=editor.id
    )

    assert success
    assert build_announcement_request(event, webhook_for_irc) == expected


# helpers


@pytest.fixture(scope='module')
def scope() -> SnippetScope:
    return SnippetScope.for_site('acme-2019-website')


@pytest.fixture(scope='module')
def editor(make_user):
    return make_user('Dr.Schnipsel')


@pytest.fixture(scope='module')
def created_version_and_event(scope: SnippetScope, editor):
    name = 'team_intro'
    body = 'some body'

    return snippet_service.create_snippet(scope, name, 'en', editor.id, body)


@pytest.fixture(scope='module')
def updated_version_and_event(created_version_and_event, editor):
    created_version, creation_event = created_version_and_event

    body = 'another body'

    return snippet_service.update_snippet(
        created_version.snippet_id, editor.id, body
    )
