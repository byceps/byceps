"""
byceps.services.authn.login.blueprints.admin.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import structlog

from byceps.services.authn import authn_service
from byceps.services.authn.errors import UserAuthenticationFailedError
from byceps.services.authn.events import UserLoggedInToAdminEvent
from byceps.services.authn.session import authn_session_service
from byceps.services.user.models import Password, User
from byceps.util import user_session
from byceps.util.authz import get_permissions_for_user
from byceps.util.result import Err, Ok, Result


log = structlog.get_logger()


class AuthorizationFailedError:
    pass


def log_in_user(
    username: str, password: Password, permanent: bool, ip_address: str | None
) -> Result[
    tuple[User, UserLoggedInToAdminEvent],
    UserAuthenticationFailedError | AuthorizationFailedError,
]:
    match authn_service.authenticate(username, password):
        case Ok(user):
            pass
        case Err(e):
            log.info(
                'User authentication for login to administration failed',
                username=username,
                error=str(e),
            )
            return Err(e)

    # Authentication succeeded.

    if 'admin.access' not in get_permissions_for_user(user.id):
        # The user lacks the permission required to enter the admin area.
        log.info(
            'User authorization for login to administration failed',
            user_id=str(user.id),
            screen_name=user.screen_name,
        )
        return Err(AuthorizationFailedError())

    # Authorization succeeded.

    auth_token, logged_in_event = authn_session_service.log_in_user_to_admin(
        user, ip_address
    )
    user_session.start(user.id, auth_token, permanent=permanent)

    log.info(
        'User logged in to administration',
        user_id=str(user.id),
        screen_name=user.screen_name,
    )

    return Ok((user, logged_in_event))


def log_out_user(user: User) -> None:
    user_session.end()

    log.info(
        'User logged out of administration',
        user_id=str(user.id),
        screen_name=user.screen_name,
    )
