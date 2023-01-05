"""
:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Any

from flask import Flask
from flask_babel import Babel
from jinja2.sandbox import ImmutableSandboxedEnvironment
import pytest

from byceps.util.templatefilters import dim, fallback


def test_dim():
    filters = {'dim': dim}
    context = {'value': 'not <em>that</em> relevant'}
    actual = render_template('{{ value|dim }}', filters, context)
    assert (
        actual
        == '<span class="dimmed">not &lt;em&gt;that&lt;/em&gt; relevant</span>'
    )


@pytest.mark.parametrize(
    'source, context, expected',
    [
        (
            # Escape value.
            '{{ value|fallback }}',
            {'value': 'Hello from the <em>other</em> side.'},
            'Hello from the &lt;em&gt;other&lt;/em&gt; side.',
        ),
        (
            # Ignore fallback if value is available.
            '{{ value|fallback("goodbye") }}',
            {'value': 'Hello from the <em>other</em> side.'},
            'Hello from the &lt;em&gt;other&lt;/em&gt; side.',
        ),
        (
            # Use default fallback if value is empty string.
            '{{ value|fallback }}',
            {'value': ''},
            '<span class="dimmed">not specified</span>',
        ),
        (
            # Use custom fallback if value is empty string.
            '{{ value|fallback("dunno") }}',
            {'value': ''},
            '<span class="dimmed">dunno</span>',
        ),
        (
            # Use default fallback if name is undefined.
            '{{ value|fallback }}',
            {},  # `Undefined` in template
            '<span class="dimmed">not specified</span>',
        ),
        (
            # Use custom, escaped fallback if name is undefined.
            '{{ value|fallback("<b>Nothing</b> here!") }}',
            {},  # `Undefined` in template
            '<span class="dimmed">&lt;b&gt;Nothing&lt;/b&gt; here!</span>',
        ),
    ],
)
def test_fallback(source: str, context: dict[str, Any], expected: bool):
    filters = {'fallback': fallback}

    with create_app_with_babel().test_request_context():
        assert render_template(source, filters, context) == expected


def create_app_with_babel() -> Flask:
    app = Flask(__name__)
    Babel(app)
    return app


def render_template(
    source: str, filters: dict[str, Any], context: dict[str, Any]
) -> str:
    env = ImmutableSandboxedEnvironment(autoescape=True)
    env.filters.update(filters)
    template = env.from_string(source)
    return template.render(**context)
