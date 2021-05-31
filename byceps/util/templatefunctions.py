"""
byceps.util.templatefunctions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provide and register custom template global functions.

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import babel
from flask_babel import get_locale, get_timezone


def register(app):
    """Make functions available as global functions in templates."""
    functions = [
        (_format_date, 'format_date'),
        (_format_datetime, 'format_datetime'),
        (_format_time, 'format_time'),
        (_format_number, 'format_number'),
    ]

    for f, name in functions:
        app.add_template_global(f, name)


def _format_date(*args) -> str:
    return babel.dates.format_date(*args, locale=get_locale())


def _format_datetime(*args) -> str:
    return babel.dates.format_datetime(
        *args, locale=get_locale(), tzinfo=get_timezone()
    )


def _format_time(*args) -> str:
    return babel.dates.format_time(
        *args, locale=get_locale(), tzinfo=get_timezone()
    )


def _format_number(*args) -> str:
    return babel.numbers.format_number(*args, locale=get_locale())
