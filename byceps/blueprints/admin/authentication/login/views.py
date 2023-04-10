"""
byceps.blueprints.admin.authentication.login.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from flask import abort, g, redirect, request
from flask_babel import gettext
import structlog

from .....services.authentication import authn_service
from .....services.authentication.errors import AuthenticationFailed
from .....services.authentication.session import authn_session_service
from .....services.authentication.session.authn_session_service import (
    UserLoggedIn,
)
from .....services.user.models.user import User
from .....signals import auth as auth_signals
from .....util.authorization import get_permissions_for_user
from .....util.framework.blueprint import create_blueprint
from .....util.framework.flash import flash_notice, flash_success
from .....util.framework.templating import templated
from .....util.result import Err, Ok, Result
from .....util import user_session
from .....util.views import redirect_to, respond_no_content

from .forms import LogInForm


log = structlog.get_logger()


blueprint = create_blueprint('authentication_login_admin', __name__)


class AuthorizationFailed:
    pass


@blueprint.get('/log_in')
@templated
def log_in_form():
    """Show form to log in."""
    if g.user.authenticated:
        flash_notice(
            gettext(
                'You are already logged in as "%(screen_name)s".',
                screen_name=g.user.screen_name,
            )
        )
        return redirect('/')

    form = LogInForm()

    return {'form': form}


@blueprint.post('/log_in')
@respond_no_content
def log_in():
    """Allow the user to authenticate with e-mail address and password."""
    if g.user.authenticated:
        return

    form = LogInForm(request.form)

    username = form.username.data.strip()
    password = form.password.data
    permanent = form.permanent.data
    if not all([username, password]):
        abort(401)

    log_in_result = _log_in_user(username, password, permanent)
    if log_in_result.is_err():
        abort(403)

    user, logged_in_event = log_in_result.unwrap()

    flash_success(
        gettext(
            'Successfully logged in as %(screen_name)s.',
            screen_name=user.screen_name,
        )
    )

    auth_signals.user_logged_in.send(None, event=logged_in_event)


def _log_in_user(
    username: str, password: str, permanent: bool
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
        user.id, ip_address=request.remote_addr
    )
    user_session.start(user.id, auth_token, permanent=permanent)

    log.info(
        'User logged in',
        scope='admin',
        user_id=str(user.id),
        screen_name=user.screen_name,
    )

    return Ok((user, logged_in_event))


@blueprint.get('/log_out')
@templated
def log_out_form():
    """Show form to log out."""
    if not g.user.authenticated:
        return redirect('/')


@blueprint.post('/log_out')
def log_out():
    """Log out user by deleting the corresponding cookie."""
    user_session.end()

    log.info(
        'User logged out',
        scope='admin',
        user_id=str(g.user.id),
        screen_name=g.user.screen_name,
    )

    flash_success(gettext('Successfully logged out.'))
    return redirect_to('.log_in_form')
