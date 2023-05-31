"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""


from flask import Flask

from byceps.announce.connections import build_announcement_request
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
from byceps.typing import UserID

from tests.helpers import generate_uuid

from .helpers import build_announcement_request_for_irc, now


OCCURRED_AT = now()
EDITOR_ID = UserID(generate_uuid())
SCOPE = SnippetScope.for_site(SiteID('acme-2019-website'))
SNIPPET_ID = SnippetID(generate_uuid())
SNIPPET_VERSION_ID = SnippetVersionID(generate_uuid())


def test_announce_snippet_created(app: Flask, webhook_for_irc):
    expected_text = (
        'Dr.Schnipsel hat das Snippet "team_intro" '
        'im Scope "site/acme-2019-website" angelegt.'
    )
    expected = build_announcement_request_for_irc(expected_text)

    event = SnippetCreatedEvent(
        occurred_at=OCCURRED_AT,
        initiator_id=EDITOR_ID,
        initiator_screen_name='Dr.Schnipsel',
        snippet_id=SNIPPET_ID,
        scope=SCOPE,
        snippet_name='team_intro',
        snippet_version_id=SNIPPET_VERSION_ID,
    )

    assert build_announcement_request(event, webhook_for_irc) == expected


def test_announce_snippet_updated(app: Flask, webhook_for_irc):
    expected_text = (
        'Dr.Schnipsel hat das Snippet "team_intro" '
        'im Scope "site/acme-2019-website" aktualisiert.'
    )
    expected = build_announcement_request_for_irc(expected_text)

    event = SnippetUpdatedEvent(
        occurred_at=OCCURRED_AT,
        initiator_id=EDITOR_ID,
        initiator_screen_name='Dr.Schnipsel',
        snippet_id=SNIPPET_ID,
        scope=SCOPE,
        snippet_name='team_intro',
        snippet_version_id=SNIPPET_VERSION_ID,
    )

    assert build_announcement_request(event, webhook_for_irc) == expected


def test_announce_snippet_deleted(app: Flask, webhook_for_irc):
    expected_text = (
        'Dr.Schnipsel hat das Snippet "outdated_info" '
        'im Scope "site/acme-2019-website" gelöscht.'
    )
    expected = build_announcement_request_for_irc(expected_text)

    event = SnippetDeletedEvent(
        occurred_at=OCCURRED_AT,
        initiator_id=EDITOR_ID,
        initiator_screen_name='Dr.Schnipsel',
        snippet_id=SNIPPET_ID,
        scope=SCOPE,
        snippet_name='outdated_info',
    )

    assert build_announcement_request(event, webhook_for_irc) == expected