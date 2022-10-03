"""
byceps.announce.text_assembly.snippet
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce snippet events.

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import gettext

from ...events.snippet import SnippetCreated, SnippetDeleted, SnippetUpdated
from ...services.snippet.transfer.models import Scope

from ._helpers import get_screen_name_or_fallback, with_locale


@with_locale
def assemble_text_for_snippet_created(event: SnippetCreated) -> str:
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )

    return gettext(
        '%(initiator_screen_name)s has created snippet "%(snippet_name)s" in scope "%(scope)s".',
        initiator_screen_name=initiator_screen_name,
        snippet_name=event.snippet_name,
        scope=_get_scope_label(event.scope),
    )


@with_locale
def assemble_text_for_snippet_updated(event: SnippetUpdated) -> str:
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )

    return gettext(
        '%(initiator_screen_name)s has updated snippet "%(snippet_name)s" in scope "%(scope)s".',
        initiator_screen_name=initiator_screen_name,
        snippet_name=event.snippet_name,
        scope=_get_scope_label(event.scope),
    )


@with_locale
def assemble_text_for_snippet_deleted(event: SnippetDeleted) -> str:
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )

    return gettext(
        '%(initiator_screen_name)s has deleted snippet "%(snippet_name)s" in scope "%(scope)s".',
        initiator_screen_name=initiator_screen_name,
        snippet_name=event.snippet_name,
        scope=_get_scope_label(event.scope),
    )


def _get_scope_label(scope: Scope) -> str:
    return scope.type_ + '/' + scope.name
