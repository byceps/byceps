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

    # Render quotes with optional author.
    def render_quote(name, value, options, parent, context):
        intro = ''
        if 'author' in options:
            author = options['author']
            intro = '<p class="quote-intro"><cite>{}</cite> schrieb:</p>\n' \
                .format(author)
        return '{}<blockquote>{}</blockquote>'.format(intro, value)
    parser.add_formatter('quote', render_quote, strip=True)

    return parser.format(value)
