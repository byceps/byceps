"""
:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.country import service as country_service


@pytest.mark.parametrize(
    'name, alpha2, alpha3',
    [
        ('Deutschland', 'DE', 'DEU'),
        ('Österreich' , 'AT', 'AUT'),
    ],
)
def test_get_countries_contains_country(site_app, name, alpha2, alpha3):
    countries = country_service.get_countries()

    country = find_by_name(countries, name)

    assert country is not None
    assert country.name == name
    assert country.alpha2 == alpha2
    assert country.alpha3 == alpha3


def test_get_country_names_contains_selected_items(site_app):
    actual = country_service.get_country_names()

    some_expected = frozenset([
        'Belgien',
        'Dänemark',
        'Deutschland',
        'Vereinigtes Königreich Großbritannien und Nordirland',
        'Frankreich',
        'Niederlande',
        'Österreich',
        'Schweiz',
    ])

    assert frozenset(actual).issuperset(some_expected)


def test_get_country_names_contains_no_duplicates(site_app):
    actual = country_service.get_country_names()

    assert len(actual) == len(set(actual))


# helpers


def find_by_name(countries, name):
    """Return the first country with that name, or `None` if none matches."""
    for country in countries:
        if country.name == name:
            return country
