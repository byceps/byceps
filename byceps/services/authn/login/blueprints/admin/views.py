"""
byceps.services.authn.login.blueprints.admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import g, request
from flask_babel import gettext
from secret_type import secret

from byceps.services.authn import signals as authn_signals
from byceps.services.user import user_service
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.flash import flash_notice
from byceps.util.framework.templating import templated
from byceps.util.result import Err, Ok
from byceps.util.views import redirect_to

from . import service
from .forms import LogInForm


blueprint = create_blueprint('authn_login_admin', __name__)


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

    users_exist = user_service.do_users_exist()

    return {
        'form': form,
        'users_exist': users_exist,
    }


@blueprint.post('/log_in')
def log_in():
    """Allow the user to authenticate with e-mail address and password."""
    if g.user.authenticated:
        return redirect_to('core_admin.homepage')

    form = LogInForm(request.form)
    if not form.validate():
        return log_in_form(form)

    username = form.username.data.strip()
    password = secret(form.password.data)
    permanent = form.permanent.data

    match service.log_in_user(
        username, password, permanent, request.remote_addr
    ):
        case Ok((_, logged_in_event)):
            pass
        case Err(_):
            form.form_errors.append(gettext('Login failed.'))
            return log_in_form(form)

    authn_signals.user_logged_in_to_admin.send(None, event=logged_in_event)

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
    service.log_out_user(g.user.as_user())

    return redirect_to('.log_in_form')
