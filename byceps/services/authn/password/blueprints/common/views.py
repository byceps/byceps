"""
byceps.services.authn.password.blueprints.common.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, g, request
from flask_babel import gettext
from secret_type import secret

from byceps.services.authn.password import (
    authn_password_reset_service,
    authn_password_service,
)
from byceps.services.authn import signals as authn_signals
from byceps.services.email import email_config_service, email_service
from byceps.services.email.models import NameAndAddress
from byceps.services.global_setting import global_setting_service
from byceps.services.user import user_service
from byceps.services.verification_token import verification_token_service
from byceps.services.verification_token.models import PasswordResetToken
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.flash import flash_error, flash_success
from byceps.util.framework.templating import templated
from byceps.util.views import redirect_to

from .forms import RequestResetForm, ResetForm, UpdateForm


blueprint = create_blueprint('authn_password', __name__)


# -------------------------------------------------------------------- #
# password update


@blueprint.get('/update')
@templated
def update_form(erroneous_form=None):
    """Show a form to update the current user's password."""
    _get_current_user_or_404()

    form = erroneous_form if erroneous_form else UpdateForm()

    return {'form': form}


@blueprint.post('/')
def update():
    """Update the current user's password."""
    user = _get_current_user_or_404()

    form = UpdateForm(request.form)

    if not form.validate():
        return update_form(form)

    password = secret(form.new_password.data)

    event = authn_password_service.update_password_hash(user, password, user)

    authn_signals.password_updated.send(None, event=event)

    flash_success(gettext('Password has been updated. Please log in again.'))

    return _redirect_to_login_form()


# -------------------------------------------------------------------- #
# password reset


@blueprint.get('/reset/request')
@templated
def request_reset_form(erroneous_form=None):
    """Show a form to request a password reset."""
    form = erroneous_form if erroneous_form else RequestResetForm()

    return {'form': form}


@blueprint.post('/reset/request')
def request_reset():
    """Request a password reset."""
    form = RequestResetForm(request.form)
    if not form.validate():
        return request_reset_form(form)

    screen_name = form.screen_name.data.strip()
    user = user_service.find_user_by_screen_name(screen_name)

    if (user is None) or user.deleted:
        flash_error(
            gettext(
                'Username "%(screen_name)s" is unknown.',
                screen_name=screen_name,
            )
        )
        return request_reset_form(form)

    email_address = user_service.get_email_address_data(user.id)

    if email_address.address is None:
        flash_error(
            gettext(
                'No email address is set for user "%(screen_name)s".',
                screen_name=screen_name,
            )
        )
        return request_reset_form(form)

    if not email_address.verified:
        flash_error(
            gettext(
                'The email address for user "%(screen_name)s" has not been verified.',
                screen_name=screen_name,
            )
        )
        if g.app_mode.is_admin():
            return request_reset_form(form)
        else:
            return redirect_to('user_email_address.request_confirmation_email')

    if user.suspended:
        flash_error(
            gettext(
                'User "%(screen_name)s" has been suspended.',
                screen_name=screen_name,
            )
        )
        return request_reset_form(form)

    sender = _get_sender()

    authn_password_reset_service.prepare_password_reset(
        user, email_address.address, request.url_root, sender
    )

    flash_success(
        gettext(
            'A link to set a new password for user "%(screen_name)s" '
            'has been sent to the corresponding email address.',
            screen_name=user.screen_name,
        )
    )
    return request_reset_form()


def _get_sender() -> NameAndAddress:
    if g.app_mode.is_site():
        email_config = email_config_service.get_config(g.brand_id)
        return email_config.sender
    elif g.app_mode.is_admin():
        address_str = global_setting_service.find_setting_value(
            'admin_email_sender'
        )
        if not address_str:
            address_str = 'BYCEPS <noreply@byceps.example>'

        parse_result = email_service.parse_address(address_str)
        if parse_result.is_err():
            abort(500, 'Could not parse admin email sender address')

        return parse_result.unwrap()
    else:
        abort(500, 'Unexpected app mode, cannot obtain email sender')


@blueprint.get('/reset/token/<token>')
@templated
def reset_form(token, erroneous_form=None):
    """Show a form to reset the current user's password."""
    _verify_reset_token(token)

    form = erroneous_form if erroneous_form else ResetForm()

    return {
        'form': form,
        'token': token,
    }


@blueprint.post('/reset/token/<token>')
def reset(token):
    """Reset the current user's password."""
    reset_token = _verify_reset_token(token)

    form = ResetForm(request.form)
    if not form.validate():
        return reset_form(token, form)

    password = secret(form.new_password.data)

    event = authn_password_reset_service.reset_password(reset_token, password)

    authn_signals.password_updated.send(None, event=event)

    flash_success(gettext('Password has been updated.'))

    return _redirect_to_login_form()


def _verify_reset_token(token: str) -> PasswordResetToken:
    reset_token = verification_token_service.find_for_password_reset_by_token(
        token
    )

    if (reset_token is None) or verification_token_service.is_expired(
        reset_token
    ):
        flash_error(
            gettext(
                'Invalid token. A token expires after %(hours)s hours.',
                hours=24,
            )
        )
        abort(404)

    user = reset_token.user
    if user.suspended or user.deleted:
        flash_error(gettext('No valid token specified.'))
        abort(404)

    return reset_token


# -------------------------------------------------------------------- #
# helpers


def _get_current_user_or_404():
    user = g.user
    if not user.authenticated:
        abort(404)

    return user


def _redirect_to_login_form():
    if g.app_mode.is_admin():
        return redirect_to('authn_login_admin.log_in_form')
    else:
        return redirect_to('authn_login.log_in_form')
