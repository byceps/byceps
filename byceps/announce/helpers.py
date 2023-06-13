"""
byceps.announce.helpers
~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from functools import wraps

from flask_babel import force_locale, gettext

from byceps.events.base import _BaseEvent
from byceps.services.webhooks.models import OutgoingWebhook
from byceps.util.l10n import get_default_locale

from .connections import get_name_for_event


def get_screen_name_or_fallback(screen_name: str | None) -> str:
    """Return the screen name or a fallback value."""
    return screen_name if screen_name else gettext('Someone')


def with_locale(handler):
    @wraps(handler)
    def wrapper(*args, **kwargs):
        locale = get_default_locale()
        with force_locale(locale):
            return handler(*args, **kwargs)

    return wrapper


def matches_selectors(
    event: _BaseEvent,
    webhook: OutgoingWebhook,
    attribute_name: str,
    actual_value: str,
) -> bool:
    event_name = get_name_for_event(event)
    if event_name not in webhook.event_types:
        # This should not happen as only webhooks supporting this
        # event type should have been selected before calling an
        # event announcement handler.
        return False

    event_filter = webhook.event_filters.get(event_name)
    if event_filter is None:
        return True

    allowed_values = event_filter.get(attribute_name)
    return (allowed_values is None) or (actual_value in allowed_values)
