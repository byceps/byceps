"""
byceps.util.templatefilters
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provide and register custom template filters.

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from flask import current_app
from jinja2 import evalcontextfilter, Markup
from jinja2.filters import do_default, do_trim
import pendulum

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


def local_tz_to_utc(dt: datetime):
    tz_str = _get_timezone()

    return (pendulum.instance(dt)
        .set(tz=tz_str)
        .in_tz(pendulum.UTC)
        # Keep SQLAlchemy from converting it to another zone.
        .replace(tzinfo=None))


def utc_to_local_tz(dt: datetime) -> datetime:
    """Convert naive date/time object from UTC to configured time zone."""
    tz_str = _get_timezone()
    return pendulum.instance(dt).in_tz(tz_str)


def _get_timezone() -> str:
    return current_app.config['TIMEZONE']


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
