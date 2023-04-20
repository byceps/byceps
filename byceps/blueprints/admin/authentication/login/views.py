"""
byceps.blueprints.admin.authentication.login.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import g, request
from flask_babel import gettext

from byceps.signals import auth as auth_signals
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.flash import flash_notice, flash_success
from byceps.util.framework.templating import templated
from byceps.util.views import redirect_to

from . import service
from .forms import LogInForm


blueprint = create_blueprint('authentication_login_admin', __name__)


class AuthorizationFailed:
    pass


@blueprint.get('/log_in')
@templated
def log_in_form(erroneous_form=None):
    """Show form to log in."""
    if g.user.authenticated:
        flash_notice(
            gettext(
                'You are already logged in as "%(screen_name)s".',
                screen_name=g.user.screen_name,
            )
        )
        return redirect_to('core_admin.homepage')

    form = erroneous_form if erroneous_form else LogInForm()

    return {'form': form}


@blueprint.post('/log_in')
def log_in():
    """Allow the user to authenticate with e-mail address and password."""
    if g.user.authenticated:
        return

    form = LogInForm(request.form)
    if not form.validate():
        return log_in_form(form)

    username = form.username.data.strip()
    password = form.password.data
    permanent = form.permanent.data

    log_in_result = service.log_in_user(
        username, password, permanent, ip_address=request.remote_addr
    )
    if log_in_result.is_err():
        form.form_errors.append(gettext('Login failed.'))
        return log_in_form(form)

    user, logged_in_event = log_in_result.unwrap()

    flash_success(
        gettext(
            'Successfully logged in as %(screen_name)s.',
            screen_name=user.screen_name,
        )
    )

    auth_signals.user_logged_in.send(None, event=logged_in_event)

    return redirect_to('core_admin.homepage')


@blueprint.get('/log_out')
@templated
def log_out_form():
    """Show form to log out."""
    if not g.user.authenticated:
        return redirect_to('core_admin.homepage')


@blueprint.post('/log_out')
def log_out():
    """Log out user by deleting the corresponding cookie."""
    service.log_out_user(g.user)

    flash_success(gettext('Successfully logged out.'))
    return redirect_to('.log_in_form')
