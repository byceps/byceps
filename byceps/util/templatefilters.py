"""
byceps.util.templatefilters
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provide and register custom template filters.

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from jinja2 import evalcontextfilter, Markup
from jinja2.filters import do_default, do_trim

from .datetime import format as dateformat
from . import money


@evalcontextfilter
def dim(eval_ctx, value):
    """Render value in a way so that it looks dimmed."""
    dimmed = _dim(value)
    return _wrap_markup_on_autoescape(eval_ctx, dimmed)


def _dim(value):
    return '<span class="dimmed">{}</span>'.format(value)


@evalcontextfilter
def fallback(eval_ctx, value, fallback='nicht angegeben'):
    defaulted = do_trim(do_default(value, '', True))
    result = value if defaulted else _dim(fallback)
    return _wrap_markup_on_autoescape(eval_ctx, result)


def _wrap_markup_on_autoescape(eval_ctx, value):
    return Markup(value) if eval_ctx.autoescape else value


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
    ]

    for f in functions:
        app.add_template_filter(f)
