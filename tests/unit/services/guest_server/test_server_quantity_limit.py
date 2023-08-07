"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.guest_server import guest_server_domain_service


@pytest.mark.parametrize(
    ('quantity', 'expected'),
    [
        (4, False),
        (5, True),
        (6, True),
    ],
)
def test_is_server_quantity_limit_reached(quantity, expected):
    actual = guest_server_domain_service.is_server_quantity_limit_reached(
        quantity
    )
    assert actual == expected
