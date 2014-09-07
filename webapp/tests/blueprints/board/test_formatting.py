# -*- coding: utf-8 -*-

from unittest import TestCase

from byceps.blueprints.board.formatting import render_html


class RenderBbcodeTestCase(TestCase):

    def test_auto_url_linking(self):
        text = 'before http://example.com/index.html after'
        expected = 'before <a href="http://example.com/index.html">http://example.com/index.html</a> after'
        self.assert_rendered_html(text, expected)

    def test_explicit_url_linking(self):
        text = 'before [url]http://example.com/index.html[/url] after'
        expected = 'before <a href="http://example.com/index.html">http://example.com/index.html</a> after'
        self.assert_rendered_html(text, expected)

    def test_labeled_url_linking(self):
        text = 'before [url=http://example.com/index.html]Example[/url] after'
        expected = 'before <a href="http://example.com/index.html">Example</a> after'
        self.assert_rendered_html(text, expected)

    def test_image(self):
        text = 'before [img]http://example.com/image.png[/img] after'
        expected = 'before <img src="http://example.com/image.png"/> after'
        self.assert_rendered_html(text, expected)

    def test_linked_image(self):
        text = 'before [url=http://example.com/index.html][img]http://example.com/image.png[/img][/url] after'
        expected = 'before <a href="http://example.com/index.html"><img src="http://example.com/image.png"/></a> after'
        self.assert_rendered_html(text, expected)

    def test_quote_without_author(self):
        text = '[quote]All your base are belong to us.[/quote]'
        expected = '<blockquote>All your base are belong to us.</blockquote>'
        self.assert_rendered_html(text, expected)

    def test_quote_with_author(self):
        text = '[quote author="CATS"]All your base are belong to us.[/quote]'
        expected = '<p class="quote-intro"><cite>CATS</cite> schrieb:</p>\n<blockquote>All your base are belong to us.</blockquote>'
        self.assert_rendered_html(text, expected)

    def assert_rendered_html(self, text, expected):
        actual = render_html(text)
        self.assertEqual(actual, expected)
