"""
byceps.blueprints.admin.authentication.login.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from typing import Optional

import structlog

from .....services.authentication import authn_service
from .....services.authentication.errors import AuthenticationFailed
from .....services.authentication.session import authn_session_service
from .....services.authentication.session.authn_session_service import (
    UserLoggedIn,
)
from .....services.user.models.user import User
from .....util.authorization import get_permissions_for_user
from .....util.result import Err, Ok, Result
from .....util import user_session


log = structlog.get_logger()


class AuthorizationFailed:
    pass


def log_in_user(
    username: str,
    password: str,
    permanent: bool,
    *,
    ip_address: Optional[str] = None,
) -> Result[
    tuple[User, UserLoggedIn], AuthenticationFailed | AuthorizationFailed
]:
    authn_result = authn_service.authenticate(username, password)
    if authn_result.is_err():
        log.info(
            'User authentication failed',
            scope='admin',
            username=username,
            error=str(authn_result.unwrap_err()),
        )
        return Err(authn_result.unwrap_err())

    user = authn_result.unwrap()

    # Authentication succeeded.

    if 'admin.access' not in get_permissions_for_user(user.id):
        # The user lacks the permission required to enter the admin area.
        log.info(
            'Admin authorization failed',
            user_id=str(user.id),
            screen_name=user.screen_name,
        )
        return Err(AuthorizationFailed())

    # Authorization succeeded.

    auth_token, logged_in_event = authn_session_service.log_in_user(
        user.id, ip_address=ip_address
    )
    user_session.start(user.id, auth_token, permanent=permanent)

    log.info(
        'User logged in',
        scope='admin',
        user_id=str(user.id),
        screen_name=user.screen_name,
    )

    return Ok((user, logged_in_event))


def log_out_user(user: User) -> None:
    user_session.end()

    log.info(
        'User logged out',
        scope='admin',
        user_id=str(user.id),
        screen_name=user.screen_name,
    )
