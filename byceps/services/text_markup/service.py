"""
byceps.services.text_markup.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from html import escape

from bbcode import Parser

try:
    from .smileys import get_smileys
except ModuleNotFoundError:
    def get_smileys():
        return []


try:
    from .smileys import replace_smileys as _replace_smileys
except ModuleNotFoundError:
    def _replace_smileys(text):
        return text


def _create_parser() -> Parser:
    """Create a customized BBcode parser."""
    parser = Parser(replace_cosmetic=False)

    _add_image_formatter(parser)
    _add_quote_formatter(parser)

    return parser


def _add_image_formatter(parser: Parser) -> None:
    """Replace image tags."""

    def render_image(name, value, options, parent, context):
        return '<img src="{}">'.format(value)

    parser.add_formatter('img', render_image, replace_links=False)


def _add_quote_formatter(parser: Parser) -> None:
    """Render quotes with optional author."""

    def render_quote(name, value, options, parent, context):
        intro = ''
        if 'author' in options:
            author = escape(options['author'])
            intro = '<p class="quote-intro"><cite>{}</cite> schrieb:</p>\n'.format(
                author
            )
        return '{}<blockquote>{}</blockquote>'.format(intro, value)

    parser.add_formatter('quote', render_quote, strip=True)


_PARSER = _create_parser()


def render_html(value: str) -> str:
    """Render text as HTML, interpreting BBcode."""
    html = _PARSER.format(value)
    html = _replace_smileys(html)
    return html
