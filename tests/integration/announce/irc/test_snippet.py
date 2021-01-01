"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

import byceps.announce.connections  # Connect signal handlers.
from byceps.services.snippet import service as snippet_service
from byceps.services.snippet.transfer.models import Scope
from byceps.signals import snippet as snippet_signals

from .helpers import assert_submitted_data, CHANNEL_ORGA_LOG, mocked_irc_bot


EXPECTED_CHANNEL = CHANNEL_ORGA_LOG


def test_announce_snippet_document_created(
    app, created_document_version_and_event
):
    expected_text = (
        'Dr.Schnipsel hat das Snippet-Dokument "overview" '
        'im Scope "site/acme-2019-website" angelegt.'
    )

    _, event = created_document_version_and_event

    with mocked_irc_bot() as mock:
        snippet_signals.snippet_created.send(None, event=event)

    assert_submitted_data(mock, EXPECTED_CHANNEL, expected_text)


def test_announce_snippet_fragment_created(
    app, created_fragment_version_and_event
):
    expected_text = (
        'Dr.Schnipsel hat das Snippet-Fragment "team_intro" '
        'im Scope "site/acme-2019-website" angelegt.'
    )

    _, event = created_fragment_version_and_event

    with mocked_irc_bot() as mock:
        snippet_signals.snippet_created.send(None, event=event)

    assert_submitted_data(mock, EXPECTED_CHANNEL, expected_text)


def test_announce_snippet_document_updated(
    app, updated_document_version_and_event
):
    expected_text = (
        'Dr.Schnipsel hat das Snippet-Dokument "overview" '
        'im Scope "site/acme-2019-website" aktualisiert.'
    )

    _, event = updated_document_version_and_event

    with mocked_irc_bot() as mock:
        snippet_signals.snippet_updated.send(None, event=event)

    assert_submitted_data(mock, EXPECTED_CHANNEL, expected_text)


def test_announce_snippet_fragment_updated(
    app, updated_fragment_version_and_event
):
    expected_text = (
        'Dr.Schnipsel hat das Snippet-Fragment "team_intro" '
        'im Scope "site/acme-2019-website" aktualisiert.'
    )

    _, event = updated_fragment_version_and_event

    with mocked_irc_bot() as mock:
        snippet_signals.snippet_updated.send(None, event=event)

    assert_submitted_data(mock, EXPECTED_CHANNEL, expected_text)


def test_announce_snippet_fragment_deleted(app, scope, editor):
    expected_text = (
        'Dr.Schnipsel hat das Snippet "old_fragment" '
        'im Scope "site/acme-2019-website" gelöscht.'
    )

    fragment_version, _ = snippet_service.create_fragment(
        scope, 'old_fragment', editor.id, 'This is old news. :('
    )

    success, event = snippet_service.delete_snippet(
        fragment_version.snippet_id, initiator_id=editor.id
    )

    assert success

    with mocked_irc_bot() as mock:
        snippet_signals.snippet_deleted.send(None, event=event)

    assert_submitted_data(mock, EXPECTED_CHANNEL, expected_text)


# helpers


@pytest.fixture(scope='module')
def scope():
    return Scope.for_site('acme-2019-website')


@pytest.fixture(scope='module')
def editor(make_user):
    return make_user('Dr.Schnipsel')


@pytest.fixture(scope='module')
def created_document_version_and_event(scope, editor):
    name = 'overview'
    title = 'some title'
    body = 'some body'

    return snippet_service.create_document(scope, name, editor.id, title, body)


@pytest.fixture(scope='module')
def created_fragment_version_and_event(scope, editor):
    name = 'team_intro'
    body = 'some body'

    return snippet_service.create_fragment(scope, name, editor.id, body)


@pytest.fixture(scope='module')
def updated_document_version_and_event(
    created_document_version_and_event, editor
):
    created_document_version, creation_event = (
        created_document_version_and_event
    )

    title = 'another title'
    body = 'another body'

    return snippet_service.update_document(
        created_document_version.snippet_id, editor.id, title, body
    )


@pytest.fixture(scope='module')
def updated_fragment_version_and_event(
    created_fragment_version_and_event, editor
):
    created_fragment_version, creation_event = (
        created_fragment_version_and_event
    )

    body = 'another body'

    return snippet_service.update_fragment(
        created_fragment_version.snippet_id, editor.id, body
    )
