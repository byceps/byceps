"""
byceps.announce.helpers
~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from functools import wraps

from flask_babel import force_locale, gettext

from byceps.services.user.models import User
from byceps.services.webhooks.models import OutgoingWebhook
from byceps.util.l10n import get_default_locale


def matches_selectors(
    event_name: str,
    webhook: OutgoingWebhook,
    attribute_name: str,
    actual_value: str,
) -> bool:
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


def get_screen_name_or_fallback(user: User | None) -> str:
    """Return the user's screen name or a fallback value."""
    if (user is None) or (user.screen_name is None):
        return gettext('Someone')

    return user.screen_name


def with_locale(handler):
    @wraps(handler)
    def wrapper(*args, **kwargs):
        locale = get_default_locale()
        with force_locale(locale):
            return handler(*args, **kwargs)

    return wrapper
