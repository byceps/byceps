"""
byceps.blueprints.site.authentication.login.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, g, redirect, request, url_for
from flask_babel import gettext

from .....services.site.models import Site
from .....services.site import site_service
from .....signals import auth as auth_signals
from .....util.framework.blueprint import create_blueprint
from .....util.framework.flash import flash_notice, flash_success
from .....util.framework.templating import templated
from .....util.views import redirect_to, respond_no_content

from .forms import LogInForm
from . import service
from .service import ConsentRequired


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

    log_in_result = service.log_in_user(
        username,
        password,
        permanent,
        g.brand_id,
        ip_address=request.remote_addr,
        site_id=g.site_id,
    )
    if log_in_result.is_err():
        err = log_in_result.unwrap_err()
        if isinstance(err, ConsentRequired):
            consent_form_url = url_for(
                'consent.consent_form', token=err.verification_token
            )
            return [('Location', consent_form_url)]
        else:
            abort(403)

    user, logged_in_event = log_in_result.unwrap()

    flash_success(
        gettext(
            'Successfully logged in as %(screen_name)s.',
            screen_name=user.screen_name,
        )
    )

    auth_signals.user_logged_in.send(None, event=logged_in_event)

    return [('Location', url_for('dashboard.index'))]


@blueprint.get('/log_out')
@templated
def log_out_form():
    """Show form to log out."""
    if not g.user.authenticated:
        return redirect('/')


@blueprint.post('/log_out')
def log_out():
    """Log out user by deleting the corresponding cookie."""
    service.log_out_user(g.user)

    flash_success(gettext('Successfully logged out.'))
    return redirect('/')


# helpers


def _is_site_login_enabled() -> bool:
    site = _get_site()
    return site.login_enabled


def _get_site() -> Site:
    return site_service.get_site(g.site_id)
