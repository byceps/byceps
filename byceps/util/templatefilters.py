"""
byceps.util.templatefilters
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provide and register custom template filters.

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import gettext
from jinja2 import pass_eval_context
from jinja2.filters import do_default, do_trim
from markupsafe import Markup

from .datetime import format as dateformat
from .datetime.timezone import utc_to_local_tz
from . import money


@pass_eval_context
def dim(eval_ctx, value):
    """Render value in a way so that it looks dimmed."""
    dimmed = _dim(value)
    return _wrap_markup_on_autoescape(eval_ctx, dimmed)


def _dim(value):
    return f'<span class="dimmed">{value}</span>'


@pass_eval_context
def fallback(eval_ctx, value, fallback=None):
    defaulted = do_trim(do_default(value, '', True))
    if defaulted:
        result = value
    else:
        if fallback is None:
            fallback = gettext('not specified')
        result = _dim(fallback)

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
        utc_to_local_tz,
    ]

    for f in functions:
        app.add_template_filter(f)
