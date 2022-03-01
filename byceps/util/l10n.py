"""
byceps.util.l10n
~~~~~~~~~~~~~~~~

Localization.

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from contextlib import contextmanager
from typing import Iterator, Optional

from babel import Locale
from flask import current_app, g, request
from flask_babel import force_locale
from wtforms import Form

from ..services.user.transfer.models import User


def get_current_user_locale() -> Optional[str]:
    """Return the locale for the current user, if available."""
    # Look for a locale on the current user object.
    user = getattr(g, 'user')
    if (user is not None) and (user.locale is not None):
        return user.locale

    if request:
        # Try to match user agent's accepted languages.
        languages = [locale.language for locale in get_locales()]
        return request.accept_languages.best_match(languages)

    return None


@contextmanager
def force_user_locale(user: User) -> Iterator[None]:
    """Execute code with the user's preferred locale."""
    locale = get_user_locale(user)
    with force_locale(locale):
        yield


def get_user_locale(user: User) -> str:
    """Return the user's preferred locale.

    If no preference is set for the user, return the app's default
    locale.
    """
    return user.locale or current_app.config['LOCALE']


BASE_LOCALE = Locale('en')


def get_locales() -> list[Locale]:
    """List available locales."""
    return [BASE_LOCALE] + current_app.babel_instance.list_translations()


class LocalizedForm(Form):

    def __init__(self, *args, **kwargs):
        locales = current_app.config['LOCALES_FORMS']
        kwargs['meta'] = {'locales': locales}
        super().__init__(*args, **kwargs)
