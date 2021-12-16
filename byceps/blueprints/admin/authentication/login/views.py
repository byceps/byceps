"""
byceps.blueprints.admin.authentication.login.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, g, redirect, request
from flask_babel import gettext

from .....services.authentication.exceptions import AuthenticationFailed
from .....services.authentication import service as authentication_service
from .....services.authentication.session import service as session_service
from .....signals import auth as auth_signals
from .....typing import UserID
from .....util.authorization import get_permissions_for_user
from .....util.framework.blueprint import create_blueprint
from .....util.framework.flash import flash_notice, flash_success
from .....util.framework.templating import templated
from .....util import user_session
from .....util.views import respond_no_content

from .forms import LogInForm


blueprint = create_blueprint('authentication_login_admin', __name__)


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

    screen_name = form.screen_name.data.strip()
    password = form.password.data
    permanent = form.permanent.data
    if not all([screen_name, password]):
        abort(401)

    try:
        user = authentication_service.authenticate(screen_name, password)
    except AuthenticationFailed:
        abort(401)

    _require_admin_access_permission(user.id)

    # Authorization succeeded.

    auth_token, event = session_service.log_in_user(
        user.id, request.remote_addr
    )
    user_session.start(user.id, auth_token, permanent=permanent)

    flash_success(
        gettext(
            'Successfully logged in as %(screen_name)s.',
            screen_name=user.screen_name,
        )
    )

    auth_signals.user_logged_in.send(None, event=event)


def _require_admin_access_permission(user_id: UserID) -> None:
    permissions = get_permissions_for_user(user_id)
    if 'admin.access' not in permissions:
        # The user lacks the admin access permission which is required
        # to enter the admin area.
        abort(403)


@blueprint.post('/log_out')
@respond_no_content
def log_out():
    """Log out user by deleting the corresponding cookie."""
    user_session.end()
    flash_success(gettext('Successfully logged out.'))
