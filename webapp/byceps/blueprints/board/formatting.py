# -*- coding: utf-8 -*-

"""
byceps.blueprints.board.formatting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

import bbcode


def render_html(value):
    """Render text as HTML, interpreting BBcode."""
    parser = bbcode.Parser(replace_cosmetic=False)

    # Replace image tags.
    def render_image(name, value, options, parent, context):
        return '<img src="{}"/>'.format(value)
    parser.add_formatter('img', render_image, replace_links=False)

    return parser.format(value)
