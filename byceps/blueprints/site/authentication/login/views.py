"""
byceps.blueprints.site.authentication.login.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, g, request, url_for

from .....services.authentication.exceptions import AuthenticationFailed
from .....services.authentication import service as authentication_service
from .....services.authentication.session import service as session_service
from .....services.consent import (
    consent_service,
    subject_service as consent_subject_service,
)
from .....services.site import service as site_service
from .....services.site.transfer.models import Site
from .....services.verification_token import (
    service as verification_token_service,
)
from .....typing import UserID
from .....util.framework.blueprint import create_blueprint
from .....util.framework.flash import flash_notice, flash_success
from .....util.framework.templating import templated
from .....util import user_session
from .....util.views import redirect_to, respond_no_content

from .forms import LoginForm


blueprint = create_blueprint('authentication.login', __name__)


# -------------------------------------------------------------------- #
# log in/out


@blueprint.route('/login')
@templated
def login_form():
    """Show login form."""
    if g.user.is_active:
        flash_notice(
            f'Du bist bereits als Benutzer "{g.user.screen_name}" angemeldet.'
        )
        return redirect_to('dashboard.index')

    if not _is_site_login_enabled():
        return {
            'login_enabled': False,
        }

    form = LoginForm()

    site = _get_site()

    return {
        'login_enabled': True,
        'form': form,
        'user_account_creation_enabled': site.user_account_creation_enabled,
    }


@blueprint.route('/login', methods=['POST'])
@respond_no_content
def login():
    """Allow the user to authenticate with e-mail address and password."""
    if g.user.is_active:
        return

    if not _is_site_login_enabled():
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

    if _is_consent_required(user.id):
        verification_token = verification_token_service.create_for_terms_consent(
            user.id
        )

        consent_form_url = url_for(
            'consent.consent_form', token=verification_token.token
        )

        return [('Location', consent_form_url)]

    # Authorization succeeded.

    auth_token = session_service.log_in_user(user.id, request.remote_addr)
    user_session.start(user.id, auth_token, permanent=permanent)
    flash_success(f'Erfolgreich eingeloggt als {user.screen_name}.')

    return [('Location', url_for('dashboard.index'))]


def _is_consent_required(user_id: UserID) -> bool:
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


# helpers


def _is_site_login_enabled() -> bool:
    site = _get_site()
    return site.login_enabled


def _get_site() -> Site:
    return site_service.get_site(g.site_id)
