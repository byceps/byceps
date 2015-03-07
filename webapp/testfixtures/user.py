# -*- coding: utf-8 -*-

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


def create_user_with_detail(number, *, screen_name=None, email_address=None,
                            enabled=True, date_of_birth=None):
    user = create_user(number, screen_name=screen_name,
                       email_address=email_address, enabled=enabled)
    detail = UserDetail(user=user)
    if date_of_birth:
        detail.date_of_birth = date_of_birth
    return user
