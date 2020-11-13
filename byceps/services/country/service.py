"""
byceps.services.country.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import codecs
from dataclasses import dataclass
import json
from typing import List

from flask import current_app


@dataclass(frozen=True)
class Country:
    name: str
    alpha2: str
    alpha3: str


def get_countries() -> List[Country]:
    """Load countries from JSON file."""
    reader = codecs.getreader('utf-8')

    path = 'services/country/resources/countries.json'
    with current_app.open_resource(path) as f:
        records = json.load(reader(f))

    return [Country(**record) for record in records]


def get_country_names() -> List[str]:
    """Return country names."""
    return [country.name for country in get_countries()]
