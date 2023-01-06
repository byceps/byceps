"""
byceps.services.text_markup.text_markup_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from html import escape

from bbcode import Parser
from flask_babel import gettext

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

    _add_code_formatter(parser)
    _add_image_formatter(parser)
    _add_quote_formatter(parser)

    return parser


def _add_code_formatter(parser: Parser) -> None:
    """Replace code tags."""

    def render_code(name, value, options, parent, context):
        return f'<pre><code class="block">{value}</code></pre>'

    parser.add_formatter(
        'code', render_code, replace_cosmetic=False, replace_links=False
    )


def _add_image_formatter(parser: Parser) -> None:
    """Replace image tags."""

    def render_image(name, value, options, parent, context):
        return f'<img src="{value}">'

    parser.add_formatter(
        'img', render_image, replace_cosmetic=False, replace_links=False
    )


def _add_quote_formatter(parser: Parser) -> None:
    """Render quotes with optional author."""

    def render_quote(name, value, options, parent, context):
        intro = ''
        if 'author' in options:
            author = escape(options['author'])
            verb = gettext('wrote')
            intro = (
                f'<p class="quote-intro"><cite>{author}</cite> {verb}:</p>\n'
            )
        return f'{intro}<blockquote>{value}</blockquote>'

    parser.add_formatter('quote', render_quote, strip=True)


_PARSER = _create_parser()


def render_html(value: str) -> str:
    """Render text as HTML, interpreting BBcode."""
    html = _PARSER.format(value)
    html = _replace_smileys(html)
    return html
