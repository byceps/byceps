"""
:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from moneyed import EUR, Money
import pytest

from byceps.services.shop.article.models import ArticleWithQuantity


@pytest.mark.parametrize(
    ('quantity', 'expected_amount'),
    [
        (1, Money('1.99', EUR)),
        (2, Money('3.98', EUR)),
        (6, Money('11.94', EUR)),
    ],
)
def test_init_with_positive_quantity(
    make_article, quantity: int, expected_amount: Money
):
    article = make_article()

    awq = ArticleWithQuantity(article, quantity)

    assert awq.article == article
    assert awq.quantity == quantity
    assert awq.amount == expected_amount


def test_init_with_zero_quantity(make_article):
    with pytest.raises(ValueError):
        ArticleWithQuantity(make_article(), 0)


def test_init_with_negative_quantity(make_article):
    with pytest.raises(ValueError):
        ArticleWithQuantity(make_article(), -1)
