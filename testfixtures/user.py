# -*- coding: utf-8 -*-

"""
testfixtures.user
~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import date

from byceps.blueprints.user.models.detail import UserDetail
from byceps.blueprints.user import service as user_service
from byceps.database import generate_uuid


def create_user(number, *, screen_name=None, email_address=None, enabled=True):
    if not screen_name:
        screen_name = 'User-{:d}'.format(number)

    if not email_address:
        email_address = 'user{:03d}@example.com'.format(number)

    user = user_service.build_user(screen_name, email_address)
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
    detail.country = 'State of Mind'
    detail.zip_code = '31337'
    detail.city = 'Atrocity'
    detail.street = 'Elite Street 1337'

    return user
