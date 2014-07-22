# -*- coding: utf-8 -*-

"""
byceps.util.l10n
~~~~~~~~~~~~~~~~

Localization.

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

import locale
import warnings


def set_locale(locale_str):
    try:
        locale.setlocale(locale.LC_ALL, locale_str)
    except:
        warnings.warn('Could not set locale to "{}".'.format(locale_str))
