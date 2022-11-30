"""
:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

import byceps.announce.connections  # Connect signal handlers.  # noqa: F401
from byceps.services.snippet import snippet_service
from byceps.services.snippet.transfer.models import Scope
from byceps.signals import snippet as snippet_signals

from .helpers import assert_submitted_data, mocked_irc_bot


def test_announce_snippet_created(app, created_version_and_event):
    expected_text = (
        'Dr.Schnipsel hat das Snippet "team_intro" '
        'im Scope "site/acme-2019-website" angelegt.'
    )

    _, event = created_version_and_event

    with mocked_irc_bot() as mock:
        snippet_signals.snippet_created.send(None, event=event)

    assert_submitted_data(mock, expected_text)


def test_announce_snippet_updated(app, updated_version_and_event):
    expected_text = (
        'Dr.Schnipsel hat das Snippet "team_intro" '
        'im Scope "site/acme-2019-website" aktualisiert.'
    )

    _, event = updated_version_and_event

    with mocked_irc_bot() as mock:
        snippet_signals.snippet_updated.send(None, event=event)

    assert_submitted_data(mock, expected_text)


def test_announce_snippet_deleted(app, scope, editor):
    expected_text = (
        'Dr.Schnipsel hat das Snippet "outdated_info" '
        'im Scope "site/acme-2019-website" gelöscht.'
    )

    version, _ = snippet_service.create_snippet(
        scope, 'outdated_info', editor.id, 'This is old news. :('
    )

    success, event = snippet_service.delete_snippet(
        version.snippet_id, initiator_id=editor.id
    )

    assert success

    with mocked_irc_bot() as mock:
        snippet_signals.snippet_deleted.send(None, event=event)

    assert_submitted_data(mock, expected_text)


# helpers


@pytest.fixture(scope='module')
def scope():
    return Scope.for_site('acme-2019-website')


@pytest.fixture(scope='module')
def editor(make_user):
    return make_user('Dr.Schnipsel')


@pytest.fixture(scope='module')
def created_version_and_event(scope, editor):
    name = 'team_intro'
    body = 'some body'

    return snippet_service.create_snippet(scope, name, editor.id, body)


@pytest.fixture(scope='module')
def updated_version_and_event(created_version_and_event, editor):
    created_version, creation_event = (
        created_version_and_event
    )

    body = 'another body'

    return snippet_service.update_snippet(
        created_version.snippet_id, editor.id, body
    )
