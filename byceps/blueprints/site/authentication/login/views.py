"""
byceps.blueprints.site.authentication.login.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, g, redirect, request, url_for
from flask_babel import gettext
import structlog

from .....services.authentication import authn_service
from .....services.authentication.session import authn_session_service
from .....services.consent import consent_service, consent_subject_service
from .....services.site.models import Site
from .....services.site import site_service
from .....services.verification_token import verification_token_service
from .....signals import auth as auth_signals
from .....typing import UserID
from .....util.framework.blueprint import create_blueprint
from .....util.framework.flash import flash_notice, flash_success
from .....util.framework.templating import templated
from .....util import user_session
from .....util.views import redirect_to, respond_no_content

from .forms import LogInForm


log = structlog.get_logger()


blueprint = create_blueprint('authentication_login', __name__)


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
        return redirect_to('dashboard.index')

    if not _is_site_login_enabled():
        return {
            'login_enabled': False,
        }

    form = LogInForm()

    site = _get_site()

    return {
        'login_enabled': True,
        'form': form,
        'user_account_creation_enabled': site.user_account_creation_enabled,
    }


@blueprint.post('/log_in')
@respond_no_content
def log_in():
    """Allow the user to authenticate with e-mail address and password."""
    if g.user.authenticated:
        return

    if not _is_site_login_enabled():
        abort(403, 'Log in to this site is generally disabled.')

    form = LogInForm(request.form)

    username = form.username.data.strip()
    password = form.password.data
    permanent = form.permanent.data
    if not all([username, password]):
        abort(401)

    authn_result = authn_service.authenticate(username, password)
    if authn_result.is_err():
        log.info(
            'User authentication failed',
            scope='site',
            username=username,
            error=str(authn_result.unwrap_err()),
        )
        abort(401)

    user = authn_result.unwrap()

    if _is_consent_required(user.id):
        verification_token = verification_token_service.create_for_consent(
            user.id
        )

        consent_form_url = url_for(
            'consent.consent_form', token=verification_token.token
        )

        return [('Location', consent_form_url)]

    # Authorization succeeded.

    auth_token, event = authn_session_service.log_in_user(
        user.id, request.remote_addr, site_id=g.site_id
    )
    user_session.start(user.id, auth_token, permanent=permanent)

    log.info(
        'User logged in',
        scope='site',
        user_id=str(user.id),
        screen_name=user.screen_name,
    )

    flash_success(
        gettext(
            'Successfully logged in as %(screen_name)s.',
            screen_name=user.screen_name,
        )
    )

    auth_signals.user_logged_in.send(None, event=event)

    return [('Location', url_for('dashboard.index'))]


def _is_consent_required(user_id: UserID) -> bool:
    required_subject_ids = (
        consent_subject_service.get_subject_ids_required_for_brand(g.brand_id)
    )

    return not consent_service.has_user_consented_to_all_subjects(
        user_id, required_subject_ids
    )


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
        scope='site',
        user_id=str(g.user.id),
        screen_name=g.user.screen_name,
    )

    flash_success(gettext('Successfully logged out.'))
    return redirect('/')


# helpers


def _is_site_login_enabled() -> bool:
    site = _get_site()
    return site.login_enabled


def _get_site() -> Site:
    return site_service.get_site(g.site_id)
