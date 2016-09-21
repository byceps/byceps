# -*- coding: utf-8 -*-

"""
byceps.blueprints.authentication.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import abort, g, request, url_for

from ...config import get_site_mode, get_user_registration_enabled
from ...util.framework import create_blueprint, flash_error, flash_notice, \
    flash_success
from ...util.templating import templated
from ...util.views import respond_no_content

from ..terms import service as terms_service
from ..user import service as user_service
from ..verification_token import service as verification_token_service

from .forms import LoginForm
from . import service
from .service import AuthenticationFailed
from . import session as user_session


blueprint = create_blueprint('authentication', __name__)


@blueprint.before_app_request
def before_request():
    g.current_user = user_session.get_user()


@blueprint.route('/login')
@templated
def login_form():
    """Show login form."""
    logged_in = g.current_user.is_active
    if logged_in:
        flash_error('Du bist bereits als Benutzer "{}" angemeldet.',
                    g.current_user.screen_name)

    form = LoginForm()
    user_registration_enabled = get_user_registration_enabled()

    return {
        'logged_in': logged_in,
        'form': form,
        'user_registration_enabled': user_registration_enabled,
    }


@blueprint.route('/login', methods=['POST'])
@respond_no_content
def login():
    """Allow the user to authenticate with e-mail address and password."""
    if g.current_user.is_active:
        return

    form = LoginForm(request.form)

    screen_name = form.screen_name.data
    password = form.password.data
    permanent = form.permanent.data
    if not all([screen_name, password]):
        abort(403)

    # Look up user.
    user = user_service.find_user_by_screen_name(screen_name)
    if user is None:
        # User name is unknown.
        abort(403)

    # Verify credentials.
    try:
        user = service.authenticate(user, password)
    except AuthenticationFailed:
        abort(403)

    in_admin_mode = get_site_mode().is_admin()

    if in_admin_mode and not user.is_orga_for_any_brand:
        # Authenticated user must be an orga to be allowed to enter the
        # admin area but isn't.
        abort(403)

    if not in_admin_mode:
        terms_version = terms_service.get_current_version(g.party.brand)
        if not terms_service.has_user_accepted_version(user, terms_version):
            verification_token = verification_token_service \
                .find_or_create_for_terms_consent(user)
            consent_form_url = url_for('terms.consent_form',
                                       version_id=terms_version.id,
                                       token=verification_token.token)
            flash_notice(
                'Bitte <a href="{}">akzeptiere zunächst die aktuellen AGB</a>.'
                    .format(consent_form_url), text_is_safe=True)
            return

    # Authorization succeeded.

    session_token = service.find_session_token_for_user(user.id)
    if session_token is None:
        abort(500)

    user_session.start(user.id, session_token.token, permanent=permanent)
    flash_success('Erfolgreich eingeloggt als {}.', user.screen_name)


@blueprint.route('/logout', methods=['POST'])
@respond_no_content
def logout():
    """Log out user by deleting the corresponding cookie."""
    user_session.end()
    flash_success('Erfolgreich ausgeloggt.')
