"""
:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

import byceps.announce.connections  # Connect signal handlers.
from byceps.services.page import service as page_service
from byceps.signals import page as page_signals

from .helpers import assert_submitted_data, CHANNEL_INTERNAL, mocked_irc_bot


LANGUAGE_CODE = 'en'
URL_PATH = '/page'

EXPECTED_CHANNEL = CHANNEL_INTERNAL


def test_announce_page_created(app, created_version_and_event):
    expected_text = (
        'PageEditor hat die Seite "overview" '
        'in Site "acmecon-2014-website" angelegt.'
    )

    _, event = created_version_and_event

    with mocked_irc_bot() as mock:
        page_signals.page_created.send(None, event=event)

    assert_submitted_data(mock, EXPECTED_CHANNEL, expected_text)


def test_announce_page_updated(app, updated_version_and_event):
    expected_text = (
        'PageEditor hat die Seite "overview" '
        'in Site "acmecon-2014-website" aktualisiert.'
    )

    _, event = updated_version_and_event

    with mocked_irc_bot() as mock:
        page_signals.page_updated.send(None, event=event)

    assert_submitted_data(mock, EXPECTED_CHANNEL, expected_text)


def test_announce_page_deleted(app, site, editor):
    expected_text = (
        'PageEditor hat die Seite "old_page" '
        'in Site "acmecon-2014-website" gelöscht.'
    )

    version, _ = page_service.create_page(
        site.id,
        'old_page',
        LANGUAGE_CODE,
        '/page_old',
        editor.id,
        'Old news!',
        'This is old news. :(',
    )

    success, event = page_service.delete_page(
        version.page_id, initiator_id=editor.id
    )

    assert success

    with mocked_irc_bot() as mock:
        page_signals.page_deleted.send(None, event=event)

    assert_submitted_data(mock, EXPECTED_CHANNEL, expected_text)


# helpers


@pytest.fixture(scope='module')
def editor(make_user):
    return make_user('PageEditor')


@pytest.fixture(scope='module')
def created_version_and_event(site, editor):
    name = 'overview'
    title = 'some title'
    body = 'some body'

    return page_service.create_page(
        site.id, name, LANGUAGE_CODE, URL_PATH, editor.id, title, body
    )


@pytest.fixture(scope='module')
def updated_version_and_event(created_version_and_event, editor):
    created_version, _ = created_version_and_event

    title = 'another title'
    head = 'another head'
    body = 'another body'

    return page_service.update_page(
        created_version.page_id,
        LANGUAGE_CODE,
        URL_PATH,
        editor.id,
        title,
        head,
        body,
    )
