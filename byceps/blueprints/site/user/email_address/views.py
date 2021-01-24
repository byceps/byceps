"""
byceps.blueprints.site.user.email_address.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import abort, g, request
from flask_babel import gettext

from .....services.user import email_address_verification_service
from .....services.user import (
    command_service as user_command_service,
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


@blueprint.route('/confirmation_email/request')
@templated
def request_confirmation_email_form(erroneous_form=None):
    """Show a form to request the email address confirmation email for the user
    account again.
    """
    form = erroneous_form if erroneous_form else RequestConfirmationEmailForm()
    return {'form': form}


@blueprint.route('/confirmation_email/request', methods=['POST'])
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
                'Der Benutzername "%(screen_name)s" ist unbekannt.',
                screen_name=screen_name,
            )
        )
        return request_confirmation_email_form(form)

    if user.email_address is None:
        flash_error(
            gettext(
                'Für das Benutzerkonto "%(screen_name)s" ist keine E-Mail-Adresse hinterlegt.',
                screen_name=screen_name,
            )
        )
        return request_confirmation_email_form(form)

    if user.email_address_verified:
        flash_notice(
            gettext(
                'Die E-Mail-Adresse für den Benutzernamen "%(screen_name)s" wurde bereits bestätigt.',
                screen_name=user.screen_name,
            )
        )
        return request_confirmation_email_form()

    if user.suspended:
        flash_error(
            gettext(
                'Das Benutzerkonto "%(screen_name)s" ist gesperrt.',
                screen_name=screen_name,
            )
        )
        return request_confirmation_email_form()

    email_address_verification_service.send_email_address_confirmation_email(
        user.email_address, user.screen_name, user.id, g.site_id
    )

    flash_success(
        gettext(
            'Der Link zur Bestätigung der für den Benutzernamen '
            '"%(screen_name)s" hinterlegten E-Mail-Adresse '
            'wurde erneut versendet.',
            screen_name=user.screen_name,
        )
    )

    return redirect_to('.request_confirmation_email_form')


@blueprint.route('/confirmation/<token>')
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
        flash_error(gettext('Es wurde kein gültiges Token angegeben.'))
        abort(404)

    event = email_address_verification_service.confirm_email_address(
        verification_token
    )
    flash_success(gettext('Die E-Mail-Adresse wurde bestätigt.'))

    if not user.initialized:
        user_command_service.initialize_account(user.id)
        flash_success(
            gettext(
                'Das Benutzerkonto "%(screen_name)s" wurde aktiviert.',
                screen_name=user.screen_name,
            )
        )

    user_signals.email_address_confirmed.send(None, event=event)

    return redirect_to('authentication.login.login_form')
