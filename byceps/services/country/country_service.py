"""
byceps.services.country.country_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
import json

from flask import current_app


@dataclass(frozen=True, kw_only=True)
class Country:
    name: str
    alpha2: str
    alpha3: str


def get_countries() -> list[Country]:
    """Load countries from JSON file."""
    path = 'services/country/resources/countries.json'
    with current_app.open_resource(path) as f:
        records = json.load(f)

    return [Country(**record) for record in records]


def get_country_names() -> list[str]:
    """Return country names."""
    return [country.name for country in get_countries()]
