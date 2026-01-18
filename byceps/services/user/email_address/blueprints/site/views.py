"""
byceps.services.user.email_address.blueprints.site.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import g, request
from flask_babel import gettext

from byceps.services.user import (
    signals as user_signals,
    user_command_service,
    user_email_address_service,
    user_service,
)
from byceps.services.verification_token import verification_token_service
from byceps.services.verification_token.models import (
    EmailAddressChangeToken,
    EmailAddressConfirmationToken,
)
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.flash import flash_error, flash_notice, flash_success
from byceps.util.framework.templating import templated
from byceps.util.views import redirect_to

from .forms import RequestConfirmationEmailForm


blueprint = create_blueprint('user_email_address', __name__)


@blueprint.get('/confirmation_email/request')
@templated
def request_confirmation_email_form(erroneous_form=None):
    """Show a form to request the email address confirmation email for the user
    account again.
    """
    form = erroneous_form if erroneous_form else RequestConfirmationEmailForm()
    return {'form': form}


@blueprint.post('/confirmation_email/request')
def request_confirmation_email():
    """Request the email address confirmation email for the user account
    again.
    """
    form = RequestConfirmationEmailForm(request.form)
    if not form.validate():
        return request_confirmation_email_form(form)

    screen_name = form.screen_name.data.strip()
    user = user_service.find_user_by_screen_name(screen_name)

    if (user is None) or user.deleted:
        flash_error(
            gettext(
                'Username "%(screen_name)s" is unknown.',
                screen_name=screen_name,
            )
        )
        return request_confirmation_email_form(form)

    email_address = user_service.get_email_address_data(user.id)

    if email_address.address is None:
        flash_error(
            gettext(
                'No email address is set for user "%(screen_name)s".',
                screen_name=screen_name,
            )
        )
        return request_confirmation_email_form(form)

    if email_address.verified:
        flash_notice(
            gettext(
                'The email address for user "%(screen_name)s" has already been verified.',
                screen_name=user.screen_name,
            )
        )
        return request_confirmation_email_form()

    if user.suspended:
        flash_error(
            gettext(
                'User "%(screen_name)s" has been suspended.',
                screen_name=screen_name,
            )
        )
        return request_confirmation_email_form()

    user_email_address_service.send_email_address_confirmation_email_for_site(
        user, email_address.address, g.site.id
    )

    flash_success(
        gettext(
            'The link to verify the email address for user "%(screen_name)s" '
            'has been sent again.',
            screen_name=user.screen_name,
        )
    )

    return redirect_to('.request_confirmation_email_form')


@blueprint.get('/confirmation/<token>')
@templated
def confirm_form(token):
    """Show form to confirm e-mail address of the user account assigned
    with the verification token.
    """
    confirmation_token = _find_valid_confirmation_token(token)
    if not confirmation_token:
        flash_error(gettext('No valid token specified.'))
        return

    return {
        'token': confirmation_token.token,
        'email_address': confirmation_token.email_address,
    }


@blueprint.post('/confirmation/<token>')
def confirm(token):
    """Confirm e-mail address of the user account assigned with the
    verification token.
    """
    confirmation_token = _find_valid_confirmation_token(token)
    if not confirmation_token:
        return confirm_form(token)

    confirmation_result = (
        user_email_address_service.confirm_email_address_via_verification_token(
            confirmation_token
        )
    )
    if confirmation_result.is_err():
        flash_error(gettext('Email address verification failed.'))
        return redirect_to('authn_login.log_in_form')

    event = confirmation_result.unwrap()

    flash_success(gettext('Email address has been verified.'))

    user = confirmation_token.user
    if not user.initialized:
        user_command_service.initialize_account(user)
        flash_success(
            gettext(
                'User "%(screen_name)s" has been activated.',
                screen_name=user.screen_name,
            )
        )

    user_signals.email_address_confirmed.send(None, event=event)

    return redirect_to('authn_login.log_in_form')


def _find_valid_confirmation_token(
    token: str,
) -> EmailAddressConfirmationToken | None:
    confirmation_token = (
        verification_token_service.find_for_email_address_confirmation_by_token(
            token
        )
    )
    if confirmation_token is None:
        return None

    user = confirmation_token.user
    if user.suspended or user.deleted:
        return None

    return confirmation_token


@blueprint.get('/change/<token>')
@templated
def change_form(token):
    """Show form to confirm and change e-mail address of the user
    account assigned with the verification token.
    """
    change_token = _find_valid_change_token(token)
    if not change_token:
        flash_error(gettext('No valid token specified.'))
        return

    return {
        'token': change_token.token,
        'new_email_address': change_token.new_email_address,
    }


@blueprint.post('/change/<token>')
def change(token):
    """Confirm and change e-mail address of the user account assigned
    with the verification token.
    """
    change_token = _find_valid_change_token(token)
    if not change_token:
        return change_form(token)

    change_result = user_email_address_service.change_email_address(
        change_token
    )
    if change_result.is_err():
        flash_error(gettext('Email address change failed.'))
        return redirect_to('authn_login.log_in_form')

    event = change_result.unwrap()

    flash_success(gettext('Email address has been changed.'))

    user_signals.email_address_changed.send(None, event=event)

    if g.user.authenticated:
        return redirect_to('user_settings.view')
    else:
        return redirect_to('authn_login.log_in_form')


def _find_valid_change_token(token: str) -> EmailAddressChangeToken | None:
    change_token = (
        verification_token_service.find_for_email_address_change_by_token(token)
    )
    if change_token is None:
        return None

    user = change_token.user
    if user.suspended or user.deleted:
        return None

    return change_token
