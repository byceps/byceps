# -*- coding: utf-8 -*-

"""
byceps.blueprints.user.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import codecs
import json

from flask import url_for

from ...database import db
from ... import email

from .models import User
from .models.country import Country


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


def _do_users_matching_filter_exist(model_attribute, search_value):
    """Return `True` if any users match the filter.

    Comparison is done case-insensitively.
    """
    user_count = User.query \
        .filter(db.func.lower(model_attribute) == search_value.lower()) \
        .count()
    return user_count > 0


def send_email_address_confirmation_email(user, verification_token):
    confirmation_url = url_for('.confirm_email_address',
                               token=verification_token.token,
                               _external=True)

    subject = '{0.screen_name}, bitte bestätige deine E-Mail-Adresse'.format(user)
    body = (
        'Hallo {0.screen_name},\n\n'
        'bitte bestätige deine E-Mail-Adresse indem du diese URL abrufst: {1}'
    ).format(user, confirmation_url)
    recipients = [user.email_address]

    email.send(subject=subject, body=body, recipients=recipients)


def send_password_reset_email(user, verification_token):
    confirmation_url = url_for('.password_reset_form',
                               token=verification_token.token,
                               _external=True)

    subject = '{0.screen_name}, so kannst du ein neues Passwort festlegen'.format(user)
    body = (
        'Hallo {0.screen_name},\n\n'
        'du kannst ein neues Passwort festlegen indem du diese URL abrufst: {1}'
    ).format(user, confirmation_url)
    recipients = [user.email_address]

    email.send(subject=subject, body=body, recipients=recipients)
