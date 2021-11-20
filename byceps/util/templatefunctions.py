"""
byceps.util.templatefunctions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provide and register custom template global functions.

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import babel
from flask_babel import get_locale, npgettext, pgettext


def register(app):
    """Make functions available as global functions in templates."""
    functions = [
        (_format_number, 'format_number'),
        (npgettext, 'npgettext'),
        (pgettext, 'pgettext'),
    ]

    for f, name in functions:
        app.add_template_global(f, name)


def _format_number(*args) -> str:
    return babel.numbers.format_decimal(*args, locale=get_locale())
