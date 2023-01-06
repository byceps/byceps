"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.text_markup.text_markup_service import render_html


def test_auto_url_linking():
    text = 'before http://example.com/index.html after'
    expected = 'before <a rel="nofollow" href="http://example.com/index.html">http://example.com/index.html</a> after'
    assert render_html(text) == expected


def test_code_block():
    text = 'Use the source, Luke!\n[code]Do not replace ... with an ellipsis character![/code]\nSweet!'
    expected = 'Use the source, Luke!<br /><pre><code class="block">Do not replace ... with an ellipsis character!</code></pre><br />Sweet!'
    assert render_html(text) == expected


def test_explicit_url_linking():
    text = 'before [url]http://example.com/index.html[/url] after'
    expected = 'before <a rel="nofollow" href="http://example.com/index.html">http://example.com/index.html</a> after'
    assert render_html(text) == expected


def test_explicit_url_linking_applies_no_cosmetics():
    text = 'before [url]http://example.com/dash--dash.html[/url] after'
    expected = 'before <a rel="nofollow" href="http://example.com/dash--dash.html">http://example.com/dash--dash.html</a> after'
    assert render_html(text) == expected


def test_labeled_url_linking():
    text = 'before [url=http://example.com/index.html]Example[/url] after'
    expected = 'before <a rel="nofollow" href="http://example.com/index.html">Example</a> after'
    assert render_html(text) == expected


def test_image():
    text = 'before [img]http://example.com/image.png[/img] after'
    expected = 'before <img src="http://example.com/image.png"> after'
    assert render_html(text) == expected


def test_image_applies_no_cosmetics():
    text = '[img]http://example.com/double--dash.png[/img]'
    expected = '<img src="http://example.com/double--dash.png">'
    assert render_html(text) == expected


def test_linked_image():
    text = 'before [url=http://example.com/index.html][img]http://example.com/image.png[/img][/url] after'
    expected = 'before <a rel="nofollow" href="http://example.com/index.html"><img src="http://example.com/image.png"></a> after'
    assert render_html(text) == expected


def test_quote_without_author():
    text = '[quote]All your base are belong to us.[/quote]'
    expected = '<blockquote>All your base are belong to us.</blockquote>'
    assert render_html(text) == expected


def test_quote_with_author(site_app):
    text = '[quote author="CATS"]All your base are belong to us.[/quote]'
    expected = '<p class="quote-intro"><cite>CATS</cite> schrieb:</p>\n<blockquote>All your base are belong to us.</blockquote>'
    assert render_html(text) == expected


@pytest.mark.parametrize(
    'text, expected',
    [
        (
            '[quote author="foo]bar"]blah[/quote]',
            '<p class="quote-intro"><cite>foo]bar</cite> schrieb:</p>\n<blockquote>blah</blockquote>',
        ),
        (
            '[quote author="foo[bar"]blah[/quote]',
            '<p class="quote-intro"><cite>foo[bar</cite> schrieb:</p>\n<blockquote>blah</blockquote>',
        ),
        (
            '[quote author="foo][bar"]blah[/quote]',
            '<p class="quote-intro"><cite>foo][bar</cite> schrieb:</p>\n<blockquote>blah</blockquote>',
        ),
        (
            '[quote author="foo[]bar"]blah[/quote]',
            '<p class="quote-intro"><cite>foo[]bar</cite> schrieb:</p>\n<blockquote>blah</blockquote>',
        ),
        (
            '[quote author="[foobar]"]blah[/quote]',
            '<p class="quote-intro"><cite>[foobar]</cite> schrieb:</p>\n<blockquote>blah</blockquote>',
        ),
        (
            '[quote author="]foobar["]blah[/quote]',
            '<p class="quote-intro"><cite>]foobar[</cite> schrieb:</p>\n<blockquote>blah</blockquote>',
        ),
        (
            '[quote author="<AngleBracketeer>"]careful.[/quote]',
            '<p class="quote-intro"><cite>&lt;AngleBracketeer&gt;</cite> schrieb:</p>\n<blockquote>careful.</blockquote>',
        ),
    ],
)
def test_quote_with_author_whose_name_contains_square_brackets(site_app, text, expected):
    assert render_html(text) == expected
