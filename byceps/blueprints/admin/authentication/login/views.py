"""
byceps.blueprints.admin.authentication.login.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, g, redirect, request

from .....services.authentication.exceptions import AuthenticationFailed
from .....services.authentication import service as authentication_service
from .....services.authentication.session import service as session_service
from .....typing import UserID
from .....util.authorization import get_permissions_for_user
from .....util.framework.blueprint import create_blueprint
from .....util.framework.flash import flash_notice, flash_success
from .....util.framework.templating import templated
from .....util import user_session
from .....util.views import respond_no_content

from ....admin.core.authorization import AdminPermission

from .forms import LoginForm


blueprint = create_blueprint('authentication.login_admin', __name__)


@blueprint.route('/login')
@templated
def login_form():
    """Show login form."""
    if g.current_user.is_active:
        flash_notice(
            f'Du bist bereits als Benutzer "{g.current_user.screen_name}" '
            'angemeldet.'
        )
        return redirect('/')

    form = LoginForm()

    return {'form': form}


@blueprint.route('/login', methods=['POST'])
@respond_no_content
def login():
    """Allow the user to authenticate with e-mail address and password."""
    if g.current_user.is_active:
        return

    form = LoginForm(request.form)

    screen_name = form.screen_name.data.strip()
    password = form.password.data
    permanent = form.permanent.data
    if not all([screen_name, password]):
        abort(403)

    try:
        user = authentication_service.authenticate(screen_name, password)
    except AuthenticationFailed:
        abort(403)

    _require_admin_access_permission(user.id)

    # Authorization succeeded.

    auth_token = session_service.log_in_user(user.id, request.remote_addr)
    user_session.start(user.id, auth_token, permanent=permanent)
    flash_success(f'Erfolgreich eingeloggt als {user.screen_name}.')


def _require_admin_access_permission(user_id: UserID) -> None:
    permissions = get_permissions_for_user(user_id)
    if AdminPermission.access not in permissions:
        # The user lacks the admin access permission which is required
        # to enter the admin area.
        abort(403)


@blueprint.route('/logout', methods=['POST'])
@respond_no_content
def logout():
    """Log out user by deleting the corresponding cookie."""
    user_session.end()
    flash_success('Erfolgreich ausgeloggt.')
