# -*- coding: utf-8 -*-

"""
byceps.blueprints.user.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import codecs
import json

from ...database import db

from .models import Country, User


def get_countries(app):
    """Load countries from JSON file."""
    reader = codecs.getreader('utf-8')

    with app.open_resource('resources/countries.json') as f:
        records = json.load(reader(f))

    return [Country(**record) for record in records]


def get_country_names(app):
    """Return country names."""
    return [country.name for country in get_countries(app)]


def is_screen_name_already_assigned(screen_name):
    """Return `True` if a user with that screen name exists."""
    return _do_users_matching_filter_exist(User.screen_name, screen_name)


def is_email_address_already_assigned(email_address):
    """Return `True` if a user with that email address exists."""
    return _do_users_matching_filter_exist(User.email_address, email_address)


def __do_users_matching_filter_exist(model_attribute, search_value):
    """Return `True` if any users match the filter.

    Comparison is done case-insensitively.
    """
    user_count = User.query \
        .filter(db.func.lower(model_attribute) == search_value.lower()) \
        .count()
    return user_count > 0
