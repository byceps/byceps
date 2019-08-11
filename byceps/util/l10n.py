"""
byceps.util.l10n
~~~~~~~~~~~~~~~~

Localization.

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import locale
import warnings

from flask import current_app
from wtforms import Form


def set_locale(locale_str: str) -> None:
    try:
        locale.setlocale(locale.LC_ALL, locale_str)
    except locale.Error:
        warnings.warn(f'Could not set locale to "{locale_str}".')


class LocalizedForm(Form):

    def __init__(self, *args, **kwargs):
        locales = current_app.config['LOCALES_FORMS']
        kwargs['meta'] = {'locales': locales}
        super().__init__(*args, **kwargs)
