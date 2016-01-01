# -*- coding: utf-8 -*-

"""
byceps.util.templatefilters
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provide and register custom template filters.

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from jinja2 import evalcontextfilter, Markup

from . import dateformat, money


@evalcontextfilter
def dim(eval_ctx, value):
    """Render value in a way so that it looks dimmed."""
    dimmed = '<span class="dimmed">{}</span>'.format(value)
    return Markup(dimmed) if eval_ctx.autoescape else dimmed


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
        money.format_euro_amount,
    ]

    for f in functions:
        app.add_template_filter(f)
