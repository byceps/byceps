"""
byceps.blueprints.site.user.email_address.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, g, request
from flask_babel import gettext

from .....services.user import (
    command_service as user_command_service,
    email_address_verification_service,
    service as user_service,
)
from .....services.verification_token import (
    service as verification_token_service,
)
from .....signals import user as user_signals
from .....util.framework.blueprint import create_blueprint
from .....util.framework.flash import flash_error, flash_notice, flash_success
from .....util.framework.templating import templated
from .....util.views import redirect_to

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
    user = user_service.find_user_by_screen_name(
        screen_name, case_insensitive=True
    )

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

    email_address_verification_service.send_email_address_confirmation_email_for_site(
        user, email_address.address, g.site_id
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
def confirm(token):
    """Confirm e-mail address of the user account assigned with the
    verification token.
    """
    verification_token = (
        verification_token_service.find_for_email_address_confirmation_by_token(
            token
        )
    )
    if verification_token is None:
        abort(404)

    user = user_service.get_db_user(verification_token.user_id)
    if (user is None) or user.suspended or user.deleted:
        flash_error(gettext('No valid token specified.'))
        abort(404)

    try:
        event = email_address_verification_service.confirm_email_address(
            verification_token
        )
    except email_address_verification_service.EmailAddressConfirmationFailed as e:
        flash_error(gettext('Email address verification failed.'))
        return redirect_to('authentication_login.login_form')

    flash_success(gettext('Email address has been verified.'))

    if not user.initialized:
        user_command_service.initialize_account(user.id)
        flash_success(
            gettext(
                'User "%(screen_name)s" has been activated.',
                screen_name=user.screen_name,
            )
        )

    user_signals.email_address_confirmed.send(None, event=event)

    return redirect_to('authentication_login.login_form')


@blueprint.get('/change/<token>')
def change(token):
    """Confirm and change e-mail address of the user account assigned
    with the verification token.
    """
    verification_token = (
        verification_token_service.find_for_email_address_change_by_token(token)
    )
    if verification_token is None:
        abort(404)

    user = user_service.get_db_user(verification_token.user_id)
    if (user is None) or user.suspended or user.deleted:
        flash_error(gettext('No valid token specified.'))
        abort(404)

    try:
        event = email_address_verification_service.change_email_address(
            verification_token
        )
    except email_address_verification_service.EmailAddressChangeFailed as e:
        flash_error(gettext('Email address change failed.'))
        return redirect_to('authentication_login.login_form')

    flash_success(gettext('Email address has been changed.'))

    user_signals.email_address_changed.send(None, event=event)

    if g.user.authenticated:
        return redirect_to('user_settings.view')
    else:
        return redirect_to('authentication_login.login_form')
