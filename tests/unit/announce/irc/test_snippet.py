"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""


from flask import Flask
import pytest

from byceps.announce.announce import build_announcement_request
from byceps.services.site.models import SiteID
from byceps.events.snippet import (
    SnippetCreatedEvent,
    SnippetDeletedEvent,
    SnippetUpdatedEvent,
)
from byceps.services.snippet.models import (
    SnippetID,
    SnippetScope,
    SnippetVersionID,
)
from byceps.services.user.models.user import User

from tests.helpers import generate_uuid

from .helpers import assert_text, now


OCCURRED_AT = now()
SCOPE = SnippetScope.for_site(SiteID('acme-2019-website'))
SNIPPET_ID = SnippetID(generate_uuid())
SNIPPET_VERSION_ID = SnippetVersionID(generate_uuid())


def test_announce_snippet_created(app: Flask, editor: User, webhook_for_irc):
    expected_text = (
        'Dr.Schnipsel has created snippet "team_intro" (de) '
        'in scope "site/acme-2019-website".'
    )

    event = SnippetCreatedEvent(
        occurred_at=OCCURRED_AT,
        initiator=editor,
        snippet_id=SNIPPET_ID,
        scope=SCOPE,
        snippet_name='team_intro',
        snippet_version_id=SNIPPET_VERSION_ID,
        language_code='de',
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_announce_snippet_updated(app: Flask, editor: User, webhook_for_irc):
    expected_text = (
        'Dr.Schnipsel has updated snippet "team_intro" (de) '
        'in scope "site/acme-2019-website".'
    )

    event = SnippetUpdatedEvent(
        occurred_at=OCCURRED_AT,
        initiator=editor,
        snippet_id=SNIPPET_ID,
        scope=SCOPE,
        snippet_name='team_intro',
        snippet_version_id=SNIPPET_VERSION_ID,
        language_code='de',
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_announce_snippet_deleted(app: Flask, editor: User, webhook_for_irc):
    expected_text = (
        'Dr.Schnipsel has deleted snippet "outdated_info" (de) '
        'in scope "site/acme-2019-website".'
    )

    event = SnippetDeletedEvent(
        occurred_at=OCCURRED_AT,
        initiator=editor,
        snippet_id=SNIPPET_ID,
        scope=SCOPE,
        snippet_name='outdated_info',
        language_code='de',
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


# helpers


@pytest.fixture(scope='module')
def editor(make_user) -> User:
    return make_user(screen_name='Dr.Schnipsel')
