"""
byceps.util.l10n
~~~~~~~~~~~~~~~~

Localization.

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import locale
from typing import Optional
import warnings

from flask import current_app, g
from wtforms import Form


def set_locale(locale_str: str) -> None:
    try:
        locale.setlocale(locale.LC_ALL, locale_str)
    except locale.Error:
        warnings.warn(f'Could not set locale to "{locale_str}".')


def get_current_user_locale() -> Optional[str]:
    """Return the locale for the current user, if available."""
    user = getattr(g, 'user')
    if user is None:
        return None

    return user.locale


class LocalizedForm(Form):

    def __init__(self, *args, **kwargs):
        locales = current_app.config['LOCALES_FORMS']
        kwargs['meta'] = {'locales': locales}
        super().__init__(*args, **kwargs)
