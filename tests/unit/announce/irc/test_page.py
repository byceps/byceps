"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import Flask

from byceps.announce.announce import build_announcement_request
from byceps.events.page import (
    PageCreatedEvent,
    PageDeletedEvent,
    PageUpdatedEvent,
)
from byceps.services.page.models import PageID, PageVersionID
from byceps.services.site.models import SiteID
from byceps.services.user.models.user import UserID

from tests.helpers import generate_uuid

from .helpers import assert_text, now


OCCURRED_AT = now()
EDITOR_ID = UserID(generate_uuid())
PAGE_ID = PageID(generate_uuid())
PAGE_VERSION_ID = PageVersionID(generate_uuid())


def test_announce_page_created(app: Flask, webhook_for_irc):
    expected_text = (
        'PageEditor has created page "overview" (de) '
        'in site "acmecon-2014-website".'
    )

    event = PageCreatedEvent(
        occurred_at=OCCURRED_AT,
        initiator_id=EDITOR_ID,
        initiator_screen_name='PageEditor',
        page_id=PAGE_ID,
        site_id=SiteID('acmecon-2014-website'),
        page_name='overview',
        language_code='de',
        page_version_id=PAGE_VERSION_ID,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_announce_page_updated(app: Flask, webhook_for_irc):
    expected_text = (
        'PageEditor has updated page "overview" (en) '
        'in site "acmecon-2014-website".'
    )

    event = PageUpdatedEvent(
        occurred_at=OCCURRED_AT,
        initiator_id=EDITOR_ID,
        initiator_screen_name='PageEditor',
        page_id=PAGE_ID,
        site_id=SiteID('acmecon-2014-website'),
        page_name='overview',
        language_code='en',
        page_version_id=PAGE_VERSION_ID,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_announce_page_deleted(app: Flask, webhook_for_irc):
    expected_text = (
        'PageEditor has deleted page "old_page" (en) '
        'in site "acmecon-2014-website".'
    )

    event = PageDeletedEvent(
        occurred_at=OCCURRED_AT,
        initiator_id=EDITOR_ID,
        initiator_screen_name='PageEditor',
        page_id=PAGE_ID,
        site_id=SiteID('acmecon-2014-website'),
        page_name='old_page',
        language_code='en',
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)
