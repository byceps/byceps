"""
byceps.announce.handlers.snippet
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce snippet events.

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional

from flask_babel import gettext

from byceps.announce.helpers import Announcement, get_screen_name_or_fallback, with_locale
from byceps.events.snippet import SnippetCreated, SnippetDeleted, SnippetUpdated
from byceps.services.snippet.models import SnippetScope
from byceps.services.webhooks.models import OutgoingWebhook


@with_locale
def announce_snippet_created(
    event: SnippetCreated, webhook: OutgoingWebhook
) -> Optional[Announcement]:
    """Announce that a snippet has been created."""
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )

    text = gettext(
        '%(initiator_screen_name)s has created snippet "%(snippet_name)s" in scope "%(scope)s".',
        initiator_screen_name=initiator_screen_name,
        snippet_name=event.snippet_name,
        scope=_get_scope_label(event.scope),
    )

    return Announcement(text)


@with_locale
def announce_snippet_updated(
    event: SnippetUpdated, webhook: OutgoingWebhook
) -> Optional[Announcement]:
    """Announce that a snippet has been updated."""
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )

    text = gettext(
        '%(initiator_screen_name)s has updated snippet "%(snippet_name)s" in scope "%(scope)s".',
        initiator_screen_name=initiator_screen_name,
        snippet_name=event.snippet_name,
        scope=_get_scope_label(event.scope),
    )

    return Announcement(text)


@with_locale
def announce_snippet_deleted(
    event: SnippetDeleted, webhook: OutgoingWebhook
) -> Optional[Announcement]:
    """Announce that a snippet has been deleted."""
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )

    text = gettext(
        '%(initiator_screen_name)s has deleted snippet "%(snippet_name)s" in scope "%(scope)s".',
        initiator_screen_name=initiator_screen_name,
        snippet_name=event.snippet_name,
        scope=_get_scope_label(event.scope),
    )

    return Announcement(text)


def _get_scope_label(scope: SnippetScope) -> str:
    return scope.type_ + '/' + scope.name
