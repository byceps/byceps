# -*- coding: utf-8 -*-

"""
byceps.services.authentication.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from .exceptions import AuthenticationFailed
from .password import service as password_service


def authenticate(user, password):
    """Try to authenticate the user.

    Return the user object on success, or raise an exception on failure.
    """
    if not password_service.is_password_valid_for_user(user.id, password):
        # Password does not match.
        raise AuthenticationFailed()

    if not user.is_active:
        # User account is disabled.
        raise AuthenticationFailed()

    return user
