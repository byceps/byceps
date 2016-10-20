# -*- coding: utf-8 -*-

"""
bootstrap.helpers
~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.user.models.user import User

from .util import add_to_database


# -------------------------------------------------------------------- #
# users


@add_to_database
def create_user(screen_name, email_address, *, enabled=False):
    user = user_service.build_user(screen_name, email_address)
    user.enabled = enabled
    return user


def get_user(screen_name):
    return User.query.filter_by(screen_name=screen_name).one()
