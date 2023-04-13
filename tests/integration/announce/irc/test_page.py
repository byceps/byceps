"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.announce.connections import build_announcement_request
from byceps.services.page import page_service

from .helpers import build_announcement_request_for_irc


LANGUAGE_CODE = 'en'
URL_PATH = '/page'


def test_announce_page_created(
    admin_app, created_version_and_event, webhook_for_irc
):
    expected_text = (
        'PageEditor hat die Seite "overview" '
        'in Site "acmecon-2014-website" angelegt.'
    )
    expected = build_announcement_request_for_irc(expected_text)

    _, event = created_version_and_event

    assert build_announcement_request(event, webhook_for_irc) == expected


def test_announce_page_updated(
    admin_app, updated_version_and_event, webhook_for_irc
):
    expected_text = (
        'PageEditor hat die Seite "overview" '
        'in Site "acmecon-2014-website" aktualisiert.'
    )
    expected = build_announcement_request_for_irc(expected_text)

    _, event = updated_version_and_event

    assert build_announcement_request(event, webhook_for_irc) == expected


def test_announce_page_deleted(admin_app, site, editor, webhook_for_irc):
    expected_text = (
        'PageEditor hat die Seite "old_page" '
        'in Site "acmecon-2014-website" gelöscht.'
    )
    expected = build_announcement_request_for_irc(expected_text)

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
    assert build_announcement_request(event, webhook_for_irc) == expected


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
