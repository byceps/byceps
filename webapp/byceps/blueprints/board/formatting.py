# -*- coding: utf-8 -*-

"""
byceps.blueprints.board.formatting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
"""

from cgi import escape

import bbcode

try:
    from .smileys import get_smileys
except ImportError:
    get_smileys = lambda: []

try:
    from .smileys import replace_smileys
except ImportError:
    replace_smileys = lambda x: x


def create_parser():
    """Create a customized BBcode parser."""
    parser = bbcode.Parser(replace_cosmetic=False)

    # Replace image tags.
    def render_image(name, value, options, parent, context):
        return '<img src="{}"/>'.format(value)
    parser.add_formatter('img', render_image, replace_links=False)

    # Render quotes with optional author.
    def render_quote(name, value, options, parent, context):
        intro = ''
        if 'author' in options:
            author = escape(options['author'])
            intro = '<p class="quote-intro"><cite>{}</cite> schrieb:</p>\n' \
                .format(author)
        return '{}<blockquote>{}</blockquote>'.format(intro, value)
    parser.add_formatter('quote', render_quote, strip=True)

    return parser


PARSER = create_parser()


def render_html(value):
    """Render text as HTML, interpreting BBcode."""
    html = PARSER.format(value)
    html = replace_smileys(html)
    return html
