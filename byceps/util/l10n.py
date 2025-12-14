"""
byceps.util.l10n
~~~~~~~~~~~~~~~~

Localization.

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from babel import Locale
from flask import current_app, g, request
from flask_babel import format_currency
from moneyed import Money
from wtforms import Form


def get_current_user_locale() -> str | None:
    """Return the locale for the current user, if available."""
    # Look for a locale on the current user object.
    user = g.user
    if (user is not None) and (user.locale is not None):
        return user.locale.language

    if request:
        # Try to match user agent's accepted languages.
        languages = [locale.language for locale in g.locales]
        return request.accept_languages.best_match(languages)

    return None


def get_default_locale() -> Locale:
    """Return the application's default locale."""
    return Locale.parse(current_app.config['LOCALE'])


BASE_LOCALE = Locale('en')


def get_locales() -> list[Locale]:
    """List available locales."""
    return [BASE_LOCALE] + current_app.babel_instance.list_translations()


class LocalizedForm(Form):
    def __init__(self, *args, **kwargs):
        locale = current_app.config['LOCALE']
        kwargs['meta'] = {'locales': [locale]}
        super().__init__(*args, **kwargs)


def format_money(money: Money) -> str:
    """Format monetary value with amount and currency."""
    return format_currency(money.amount, money.currency.code)
