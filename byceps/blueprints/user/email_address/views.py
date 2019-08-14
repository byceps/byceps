"""
byceps.blueprints.user.email_address.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import abort, g, request

from ....services.user import email_address_confirmation_service
from ....services.user import event_service as user_event_service
from ....services.user import service as user_service
from ....services.verification_token import service as verification_token_service
from ....util.framework.blueprint import create_blueprint
from ....util.framework.flash import flash_error, flash_notice, flash_success
from ....util.framework.templating import templated
from ....util.views import redirect_to

from .. import signals

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
    user = user_service.find_user_by_screen_name(screen_name)

    if user is None:
        flash_error('Der Benutzername "{}" ist unbekannt.', screen_name)
        return request_confirmation_email_form(form)

    if user.email_address_verified:
        flash_notice(
            'Die E-Mail-Adresse für den Benutzernamen "{}" wurde bereits '
            'bestätigt.',
            user.screen_name)
        return request_confirmation_email_form()

    verification_token = verification_token_service \
        .find_or_create_for_email_address_confirmation(user.id)
    email_address_confirmation_service.send_email_address_confirmation_email(
        user.email_address, user.screen_name, verification_token, g.brand_id,
        g.site_id)

    flash_success(
        'Der Link zur Bestätigung der für den Benutzernamen "{}" '
        'hinterlegten E-Mail-Adresse wurde erneut versendet.',
        user.screen_name)

    return redirect_to('.request_confirmation_email_form')


@blueprint.route('/confirmation/<token>')
def confirm(token):
    """Confirm e-mail address of the user account assigned with the
    verification token.
    """
    verification_token = verification_token_service \
        .find_for_email_address_confirmation_by_token(token)

    if verification_token is None:
        abort(404)

    user = verification_token.user

    email_address_confirmation_service.confirm_email_address(verification_token)

    # Currently, the user's e-mail address cannot be changed, but that
    # might be allowed in the future. At that point, the verification
    # token should be extended to include the e-mail address it refers
    # to, and that value should be persisted with user event instead.
    data = {'email_address': user.email_address}
    user_event_service.create_event('email-address-confirmed', user.id, data)

    flash_success(
        'Die E-Mail-Adresse wurde bestätigt. Das Benutzerkonto "{}" ist nun aktiviert.',
        user.screen_name)
    signals.email_address_confirmed.send(None, user_id=user.id)

    return redirect_to('authentication.login_form')
