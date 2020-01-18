"""
byceps.services.country.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import codecs
from collections import namedtuple
import json
from typing import List

from flask import current_app


Country = namedtuple('Country', 'name alpha2 alpha3')


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
