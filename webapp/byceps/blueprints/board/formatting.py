# -*- coding: utf-8 -*-

"""
byceps.blueprints.board.formatting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

import bbcode


def render_html(value):
    """Render text as HTML, interpreting BBcode."""
    # No automatic link replacement for now as that interfers with
    # image embedding.
    parser = bbcode.Parser(replace_cosmetic=False, replace_links=False)

    # Replace image tags.
    parser.add_simple_formatter('img', '<img src="%(value)s"/>')

    return parser.format(value)
