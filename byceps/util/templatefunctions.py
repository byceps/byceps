"""
byceps.util.templatefunctions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provide and register custom template global functions.

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import npgettext, pgettext


def register(app):
    """Make functions available as global functions in templates."""
    functions = [
        (npgettext, 'npgettext'),
        (pgettext, 'pgettext'),
    ]

    for f, name in functions:
        app.add_template_global(f, name)
