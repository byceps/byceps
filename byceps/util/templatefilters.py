"""
byceps.util.templatefilters
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provide and register custom template filters.

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime

from flask import current_app
from jinja2 import evalcontextfilter, Markup
from jinja2.filters import do_default, do_trim
from pytz import timezone, UTC

from .datetime import format as dateformat
from . import money


@evalcontextfilter
def dim(eval_ctx, value):
    """Render value in a way so that it looks dimmed."""
    dimmed = _dim(value)
    return _wrap_markup_on_autoescape(eval_ctx, dimmed)


def _dim(value):
    return f'<span class="dimmed">{value}</span>'


@evalcontextfilter
def fallback(eval_ctx, value, fallback='nicht angegeben'):
    defaulted = do_trim(do_default(value, '', True))
    result = value if defaulted else _dim(fallback)
    return _wrap_markup_on_autoescape(eval_ctx, result)


def _wrap_markup_on_autoescape(eval_ctx, value):
    return Markup(value) if eval_ctx.autoescape else value


def separate_thousands(number: int) -> str:
    """Insert locale-specific characters to separate thousands."""
    return f'{number:n}'


def utc_to_local_tz(dt: datetime) -> datetime:
    """Convert naive date/time object from UTC to configured time zone."""
    tz = timezone(current_app.config['TIMEZONE'])
    return UTC.localize(dt).astimezone(tz)


def register(app):
    """Make functions available as template filters."""
    functions = [
        dateformat.format_custom,
        dateformat.format_date_iso,
        dateformat.format_date_short,
        dateformat.format_date_long,
        dateformat.format_datetime_iso,
        dateformat.format_datetime_short,
        dateformat.format_datetime_long,
        dateformat.format_time,
        dim,
        fallback,
        money.format_euro_amount,
        separate_thousands,
        utc_to_local_tz,
    ]

    for f in functions:
        app.add_template_filter(f)
