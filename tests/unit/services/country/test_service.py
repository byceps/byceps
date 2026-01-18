"""
:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Iterable

import pytest

from byceps.byceps_app import BycepsApp
from byceps.config.models import AppMode
from byceps.services.country import country_service
from byceps.services.country.country_service import Country


@pytest.fixture(scope='module')
def app(make_app):
    app = make_app(AppMode.site)
    with app.app_context():
        yield app


@pytest.mark.parametrize(
    ('name', 'alpha2', 'alpha3'),
    [
        ('Deutschland', 'DE', 'DEU'),
        ('Österreich', 'AT', 'AUT'),
    ],
)
def test_get_countries_contains_country(
    app: BycepsApp, name: str, alpha2: str, alpha3: str
):
    countries = country_service.get_countries()

    country = find_by_name(countries, name)

    assert country is not None
    assert country.name == name
    assert country.alpha2 == alpha2
    assert country.alpha3 == alpha3


def test_get_country_names_contains_selected_items(app: BycepsApp):
    actual = country_service.get_country_names()

    some_expected = {
        'Belgien',
        'Dänemark',
        'Deutschland',
        'Vereinigtes Königreich Großbritannien und Nordirland',
        'Frankreich',
        'Niederlande',
        'Österreich',
        'Schweiz',
    }

    assert frozenset(actual).issuperset(some_expected)


def test_get_country_names_contains_no_duplicates(app: BycepsApp):
    actual = country_service.get_country_names()

    assert len(actual) == len(set(actual))


# helpers


def find_by_name(countries: Iterable[Country], name: str):
    """Return the first country with that name, or `None` if none matches."""
    for country in countries:
        if country.name == name:
            return country
