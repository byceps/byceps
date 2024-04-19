"""
:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from moneyed import EUR, Money
import pytest

from byceps.services.shop.article import article_domain_service
from byceps.services.shop.article.models import ArticleWithQuantity


def test_calculate_total_amount_without_articles():
    with pytest.raises(ValueError):
        article_domain_service.calculate_total_amount([])


@pytest.mark.parametrize(
    ('price_strs_and_quantities', 'expected_total_str'),
    [
        (
            [
                ('0.00', 3),
            ],
            '0.00',
        ),
        (
            [
                ('1.99', 2),
            ],
            '3.98',
        ),
        (
            [
                ('1.99', 3),
                ('3.50', 1),
                ('16.25', 8),
            ],
            '139.47',
        ),
    ],
)
def test_calculate_total_amount_with_articles(
    make_article, price_strs_and_quantities, expected_total_str: str
):
    articles_with_quantities = [
        ArticleWithQuantity(make_article(price=Money(price, EUR)), quantity)
        for price, quantity in price_strs_and_quantities
    ]

    expected = Money(expected_total_str, EUR)

    actual = article_domain_service.calculate_total_amount(
        articles_with_quantities
    )

    assert actual == expected
