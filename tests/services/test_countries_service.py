# -*- coding: utf-8 -*-

"""
:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from nose2.tools import params

from byceps.application import create_app
from byceps.services import countries as countries_service


@params(
    ('Deutschland', 'DE', 'DEU'),
    ('Österreich' , 'AT', 'AUT'),
)
def test_get_countries_contains_country(name, alpha2, alpha3):
    app = create_app('test')

    with app.app_context():
        countries = countries_service.get_countries()

    country = find_by_name(countries, name)

    assert country is not None
    assert country.name == name
    assert country.alpha2 == alpha2
    assert country.alpha3 == alpha3


def test_get_country_names_contains_selected_items():
    app = create_app('test')

    with app.app_context():
        actual = countries_service.get_country_names()

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


def test_get_country_names_contains_no_duplicates():
    app = create_app('test')

    with app.app_context():
        actual = countries_service.get_country_names()

    assert len(actual) == len(set(actual))


# helpers


def find_by_name(countries, name):
    """Return the first country with that name, or `None` if none matches."""
    for country in countries:
        if country.name == name:
            return country
