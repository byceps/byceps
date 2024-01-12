"""
:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import Flask
import pytest

from byceps.blueprints.api.decorators import _extract_token_from_request


@pytest.mark.parametrize(
    ('header_value', 'expected'),
    [
        ('Bearer', None),
        ('Bearer ', None),
        ('Bearer DFD79AY9IDV9', 'DFD79AY9IDV9'),
        ('Bearer 5TPHXNPKE', '5TPHXNPKE'),
    ],
)
def test_extract_token_from_request(
    app: Flask, header_value: str, expected: str
):
    with app.test_request_context(headers=[('Authorization', header_value)]):
        assert _extract_token_from_request() == expected
