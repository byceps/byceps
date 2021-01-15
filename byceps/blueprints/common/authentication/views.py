"""
byceps.blueprints.common.authentication.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, g, redirect, request, url_for

from ....config import get_app_mode
from ....services.authentication.exceptions import AuthenticationFailed
from ....services.authentication import service as authentication_service
from ....services.authentication.session import service as session_service
from ....services.consent import (
    consent_service,
    subject_service as consent_subject_service,
)
from ....services.site import service as site_service
from ....services.verification_token import (
    service as verification_token_service,
)
from ....typing import UserID
from ....util.framework.blueprint import create_blueprint
from ....util.framework.flash import flash_notice, flash_success
from ....util.framework.templating import templated
from ....util.views import redirect_to, respond_no_content

from ...admin.core.authorization import AdminPermission

from .forms import LoginForm
from . import service, session as user_session


blueprint = create_blueprint('authentication', __name__)


# -------------------------------------------------------------------- #
# log in/out


@blueprint.route('/login')
@templated
def login_form():
    """Show login form."""
    in_admin_mode = get_app_mode().is_admin()

    if g.current_user.is_active:
        flash_notice(
            f'Du bist bereits als Benutzer "{g.current_user.screen_name}" '
            'angemeldet.'
        )
        if in_admin_mode:
            return redirect('/')
        else:
            return redirect(url_for('dashboard.index'))

    if not _is_login_enabled(in_admin_mode):
        return {
            'login_enabled': False,
        }

    form = LoginForm()
    user_account_creation_enabled = _is_user_account_creation_enabled(
        in_admin_mode
    )

    return {
        'login_enabled': True,
        'form': form,
        'user_account_creation_enabled': user_account_creation_enabled,
    }


@blueprint.route('/login', methods=['POST'])
@respond_no_content
def login():
    """Allow the user to authenticate with e-mail address and password."""
    if g.current_user.is_active:
        return

    in_admin_mode = get_app_mode().is_admin()

    if not _is_login_enabled(in_admin_mode):
        abort(403, 'Log in to this site is generally disabled.')

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

    if in_admin_mode:
        _require_admin_access_permission(user.id)

    if not in_admin_mode:
        if _is_consent_required(user.id):
            verification_token = verification_token_service.create_for_terms_consent(
                user.id
            )

            consent_form_url = url_for(
                'consent.consent_form', token=verification_token.token
            )

            return [('Location', consent_form_url)]

    # Authorization succeeded.

    session_token = session_service.get_session_token(user.id)

    session_service.record_recent_login(user.id)
    service.create_login_event(user.id, request.remote_addr)

    user_session.start(user.id, session_token.token, permanent=permanent)
    flash_success(f'Erfolgreich eingeloggt als {user.screen_name}.')

    if not in_admin_mode:
        return [('Location', url_for('dashboard.index'))]


def _require_admin_access_permission(user_id: UserID) -> None:
    permissions = service.get_permissions_for_user(user_id)
    if AdminPermission.access not in permissions:
        # The user lacks the admin access permission which is required
        # to enter the admin area.
        abort(403)


def _is_consent_required(user_id):
    required_subject_ids = consent_subject_service.get_subject_ids_required_for_brand(
        g.brand_id
    )

    return not consent_service.has_user_consented_to_all_subjects(
        user_id, required_subject_ids
    )


@blueprint.route('/logout', methods=['POST'])
@respond_no_content
def logout():
    """Log out user by deleting the corresponding cookie."""
    user_session.end()
    flash_success('Erfolgreich ausgeloggt.')


# -------------------------------------------------------------------- #
# helpers


def _is_user_account_creation_enabled(in_admin_mode):
    if in_admin_mode:
        return False

    site = _get_site()
    return site.user_account_creation_enabled


def _is_login_enabled(in_admin_mode):
    if in_admin_mode:
        return True

    site = _get_site()
    return site.login_enabled


def _get_site():
    return site_service.get_site(g.site_id)
