"""
:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from freezegun import freeze_time
import pytest

from byceps.services.shop.product import product_domain_service


@pytest.mark.parametrize(
    ('now', 'expected'),
    [
        (datetime(2014, 4, 8, 12, 0, 0), False),
        (datetime(2014, 9, 15, 17, 59, 59), False),
        (datetime(2014, 9, 15, 18, 0, 0), True),
        (datetime(2014, 9, 19, 15, 0, 0), True),
        (datetime(2014, 9, 23, 17, 59, 59), True),
        (datetime(2014, 9, 23, 18, 0, 0), False),
        (datetime(2014, 11, 4, 12, 0, 0), False),
    ],
)
def test_is_available_with_start_and_end(make_product, now, expected):
    product = make_product(
        available_from=datetime(2014, 9, 15, 18, 0, 0),
        available_until=datetime(2014, 9, 23, 18, 0, 0),
    )

    with freeze_time(now):
        assert (
            product_domain_service.is_product_available_now(product) == expected
        )


@pytest.mark.parametrize(
    ('now', 'expected'),
    [
        (datetime(2014, 4, 8, 12, 0, 0), False),
        (datetime(2014, 9, 15, 17, 59, 59), False),
        (datetime(2014, 9, 15, 18, 0, 0), True),
        (datetime(2014, 9, 19, 15, 0, 0), True),
        (datetime(2014, 9, 23, 17, 59, 59), True),
        (datetime(2014, 9, 23, 18, 0, 0), True),
        (datetime(2014, 11, 4, 12, 0, 0), True),
    ],
)
def test_is_available_with_start_and_without_end(make_product, now, expected):
    product = make_product(
        available_from=datetime(2014, 9, 15, 18, 0, 0),
    )

    with freeze_time(now):
        assert (
            product_domain_service.is_product_available_now(product) == expected
        )


@pytest.mark.parametrize(
    ('now', 'expected'),
    [
        (datetime(2014, 4, 8, 12, 0, 0), True),
        (datetime(2014, 9, 15, 17, 59, 59), True),
        (datetime(2014, 9, 15, 18, 0, 0), True),
        (datetime(2014, 9, 19, 15, 0, 0), True),
        (datetime(2014, 9, 23, 17, 59, 59), True),
        (datetime(2014, 9, 23, 18, 0, 0), False),
        (datetime(2014, 11, 4, 12, 0, 0), False),
    ],
)
def test_is_available_without_start_and_with_end(make_product, now, expected):
    product = make_product(
        available_until=datetime(2014, 9, 23, 18, 0, 0),
    )

    with freeze_time(now):
        assert (
            product_domain_service.is_product_available_now(product) == expected
        )


@pytest.mark.parametrize(
    ('now', 'expected'),
    [
        (datetime(2014, 4, 8, 12, 0, 0), True),
        (datetime(2014, 9, 15, 17, 59, 59), True),
        (datetime(2014, 9, 15, 18, 0, 0), True),
        (datetime(2014, 9, 19, 15, 0, 0), True),
        (datetime(2014, 9, 23, 17, 59, 59), True),
        (datetime(2014, 9, 23, 18, 0, 0), True),
        (datetime(2014, 11, 4, 12, 0, 0), True),
    ],
)
def test_is_available_without_start_and_without_end(
    make_product, now, expected
):
    product = make_product()

    with freeze_time(now):
        assert (
            product_domain_service.is_product_available_now(product) == expected
        )
