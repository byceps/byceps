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


def authenticate(screen_name, password):
    """Try to authenticate the user.

    Return the associated user object on success, or `None` on failure.
    """
    user = User.query.filter_by(screen_name=screen_name).first()

    if user is None:
        # User name is unknown.
        return

    if not user.is_password_valid(password):
        # Password does not match.
        return

    if not user.is_active:
        # User account is disabled.
        return

    return user


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
