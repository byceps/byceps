# -*- coding: utf-8 -*-

"""
byceps.blueprints.user.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import codecs
import json

from .models import Country


def get_countries(app):
    """Load countries from JSON file."""
    reader = codecs.getreader('utf-8')

    with app.open_resource('resources/countries.json') as f:
        records = json.load(reader(f))

    return [Country(**record) for record in records]


def get_country_names(app):
    """Return country names."""
    return [country.name for country in get_countries(app)]
