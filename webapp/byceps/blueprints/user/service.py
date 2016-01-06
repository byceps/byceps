# -*- coding: utf-8 -*-

"""
byceps.blueprints.user.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import codecs
import json

from .models import AnonymousUser, Country, User


def load_user(id, auth_token):
    """Load the user with that ID.

    Fall back to the anonymous user if the ID is unknown, the account is
    not enabled, or the auth token is invalid.
    """
    if id is None:
        return AnonymousUser()

    user = User.query.get(id)
    if (user is None) or not user.enabled:
        return AnonymousUser()

    # Validate auth token.
    if not auth_token or auth_token != str(user.auth_token):
        # Bad auth token, not logging in.
        return AnonymousUser()

    return user


def get_countries(app):
    """Load countries from JSON file."""
    reader = codecs.getreader('utf-8')

    with app.open_resource('resources/countries.json') as f:
        records = json.load(reader(f))

    return [Country(**record) for record in records]


def get_country_names(app):
    """Return country names."""
    return [country.name for country in get_countries(app)]
