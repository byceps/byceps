"""
byceps.blueprints.site.authn.login.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, g, redirect, request, url_for
from flask_babel import gettext
from secret_type import secret

from byceps.services.authn import signals as authn_signals
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.flash import flash_notice, flash_success
from byceps.util.framework.templating import templated
from byceps.util.views import redirect_to, respond_no_content

from . import service
from .forms import LogInForm
from .service import ConsentRequiredError


blueprint = create_blueprint('authn_login', __name__)


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

    if not g.site.login_enabled:
        return {
            'login_enabled': False,
        }

    form = LogInForm()

    return {
        'login_enabled': True,
        'form': form,
    }


@blueprint.post('/log_in')
@respond_no_content
def log_in():
    """Allow the user to authenticate with e-mail address and password."""
    if g.user.authenticated:
        return

    if not g.site.login_enabled:
        abort(403, 'Log in to this site is generally disabled.')

    form = LogInForm(request.form)
    if not form.validate():
        abort(401, 'Username and/or password not given')

    username = form.username.data.strip()
    password = secret(form.password.data)
    permanent = form.permanent.data

    log_in_result = service.log_in_user(
        username,
        password,
        permanent,
        g.brand_id,
        site=g.site,
        ip_address=request.remote_addr,
    )
    if log_in_result.is_err():
        err = log_in_result.unwrap_err()
        if isinstance(err, ConsentRequiredError):
            consent_form_url = url_for(
                'consent.consent_form', token=err.verification_token
            )
            return [('Location', consent_form_url)]
        else:
            abort(401, 'Authentication failed')

    user, logged_in_event = log_in_result.unwrap()

    flash_success(
        gettext(
            'Successfully logged in as %(screen_name)s.',
            screen_name=user.screen_name,
        )
    )

    authn_signals.user_logged_in.send(None, event=logged_in_event)

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
    service.log_out_user(g.user, g.site)

    flash_success(gettext('Successfully logged out.'))
    return redirect('/')
