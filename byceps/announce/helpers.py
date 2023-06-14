"""
byceps.announce.helpers
~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from functools import wraps

from flask_babel import force_locale, gettext

from byceps.util.l10n import get_default_locale


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
