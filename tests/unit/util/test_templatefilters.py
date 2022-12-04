"""
:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Any

from jinja2.sandbox import ImmutableSandboxedEnvironment
import pytest

from byceps.util.templatefilters import dim, fallback


def test_dim():
    filters = {'dim': dim}
    context = {'value': 'not that relevant'}
    actual = render_template('{{ value|dim }}', filters, context)
    assert actual == '<span class="dimmed">not that relevant</span>'


@pytest.mark.parametrize(
    'source, context, expected',
    [
        (
            '{{ value|fallback }}',
            {'value': 'Hello from the other side.'},
            'Hello from the other side.',
        ),
        (
            '{{ value|fallback("goodbye") }}',
            {'value': 'Hello from the other side.'},
            'Hello from the other side.',
        ),
        (
            '{{ value|fallback }}',
            {'value': ''},
            '<span class="dimmed">not specified</span>',
        ),
        (
            '{{ value|fallback("dunno") }}',
            {'value': ''},
            '<span class="dimmed">dunno</span>',
        ),
        (
            '{{ value|fallback }}',
            {},  # `Undefined` in template
            '<span class="dimmed">not specified</span>',
        ),
        (
            '{{ value|fallback("Nothing here!") }}',
            {},  # `Undefined` in template
            '<span class="dimmed">Nothing here!</span>',
        ),
    ],
)
def test_fallback(source: str, context: dict[str, Any], expected: bool):
    filters = {'fallback': fallback}
    assert render_template(source, filters, context) == expected


def render_template(
    source: str, filters: dict[str, Any], context: dict[str, Any]
) -> str:
    env = ImmutableSandboxedEnvironment(autoescape=True)
    env.filters.update(filters)
    template = env.from_string(source)
    return template.render(**context)
