# -*- coding: utf-8 -*-

"""
testfixtures.user
~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import date

from byceps.blueprints.user.models import User, UserDetail
from byceps.database import generate_uuid


def create_user(number, *, screen_name=None, email_address=None, enabled=True):
    if not screen_name:
        screen_name = 'User-{:d}'.format(number)

    if not email_address:
        email_address = 'user{:03d}@example.com'.format(number)

    user = User.create(screen_name, email_address, 'le_password')
    user.id = generate_uuid()
    user.enabled = enabled
    return user


def create_user_with_detail(number, *,
                            screen_name=None,
                            email_address=None,
                            enabled=True,
                            first_names='John Joseph',
                            last_name='Doe',
                            date_of_birth=None):
    user = create_user(number, screen_name=screen_name,
                       email_address=email_address, enabled=enabled)

    detail = UserDetail(user=user)
    detail.first_names = first_names
    detail.last_name = last_name
    detail.date_of_birth = (date_of_birth if date_of_birth else date(1993, 2, 15))
    detail.zip_code = '31337'
    detail.street = 'Elite Street 1337'
    detail.city = 'Atrocity'

    return user
