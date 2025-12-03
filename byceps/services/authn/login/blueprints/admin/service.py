"""
byceps.services.authn.login.blueprints.admin.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import structlog

from byceps.services.authn import authn_service
from byceps.services.authn.errors import AuthenticationFailedError
from byceps.services.authn.events import UserLoggedInEvent
from byceps.services.authn.session import authn_session_service
from byceps.services.user.models.user import Password, User
from byceps.util import user_session
from byceps.util.authz import get_permissions_for_user
from byceps.util.result import Err, Ok, Result


log = structlog.get_logger()


class AuthorizationFailed:
    pass


def log_in_user(
    username: str, password: Password, permanent: bool, ip_address: str | None
) -> Result[
    tuple[User, UserLoggedInEvent],
    AuthenticationFailedError | AuthorizationFailed,
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
        user, ip_address
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
