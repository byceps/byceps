"""
:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

import pytest

from byceps.announce.announce import build_announcement_request
from byceps.byceps_app import BycepsApp
from byceps.events.base import EventSite, EventUser
from byceps.events.page import (
    PageCreatedEvent,
    PageDeletedEvent,
    PageUpdatedEvent,
)
from byceps.services.page.models import PageID, PageVersionID

from tests.helpers import generate_uuid

from .helpers import assert_text


PAGE_ID = PageID(generate_uuid())
PAGE_VERSION_ID = PageVersionID(generate_uuid())


def test_announce_page_created(
    app: BycepsApp,
    now: datetime,
    editor: EventUser,
    site: EventSite,
    webhook_for_irc,
):
    expected_text = (
        'PageEditor has created page "overview" (de) '
        'in site "ACMECon 2014 website".'
    )

    event = PageCreatedEvent(
        occurred_at=now,
        initiator=editor,
        page_id=PAGE_ID,
        site=site,
        page_name='overview',
        language_code='de',
        page_version_id=PAGE_VERSION_ID,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_announce_page_updated(
    app: BycepsApp,
    now: datetime,
    editor: EventUser,
    site: EventSite,
    webhook_for_irc,
):
    expected_text = (
        'PageEditor has updated page "overview" (en) '
        'in site "ACMECon 2014 website".'
    )

    event = PageUpdatedEvent(
        occurred_at=now,
        initiator=editor,
        page_id=PAGE_ID,
        site=site,
        page_name='overview',
        language_code='en',
        page_version_id=PAGE_VERSION_ID,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_announce_page_deleted(
    app: BycepsApp,
    now: datetime,
    editor: EventUser,
    site: EventSite,
    webhook_for_irc,
):
    expected_text = (
        'PageEditor has deleted page "old_page" (en) '
        'in site "ACMECon 2014 website".'
    )

    event = PageDeletedEvent(
        occurred_at=now,
        initiator=editor,
        page_id=PAGE_ID,
        site=site,
        page_name='old_page',
        language_code='en',
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


# helpers


@pytest.fixture(scope='module')
def editor(make_event_user) -> EventUser:
    return make_event_user(screen_name='PageEditor')


@pytest.fixture(scope='module')
def site(make_event_site) -> EventSite:
    return make_event_site(
        id='acmecon-2014-website', title='ACMECon 2014 website'
    )
