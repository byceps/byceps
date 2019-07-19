"""
byceps.blueprints.user.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import abort, g, jsonify, request, Response

from ...config import get_site_mode
from ...services.country import service as country_service
from ...services.newsletter import service as newsletter_service
from ...services.user import command_service as user_command_service
from ...services.user import email_address_confirmation_service
from ...services.user import event_service as user_event_service
from ...services.user import service as user_service
from ...services.verification_token import service as verification_token_service
from ...util.framework.blueprint import create_blueprint
from ...util.framework.flash import flash_error, flash_notice, flash_success
from ...util.framework.templating import templated
from ...util.views import create_empty_json_response, redirect_to

from ..authentication.decorators import login_required

from .forms import DetailsForm, RequestConfirmationEmailForm
from . import signals


blueprint = create_blueprint('user', __name__)


@blueprint.route('/<uuid:user_id>.json')
def view_as_json(user_id):
    """Show selected attributes of a user's profile as JSON."""
    if get_site_mode().is_admin():
        abort(404)

    user = user_service.find_active_user(user_id, include_avatar=True)

    if user is None:
        return create_empty_json_response(404)

    return jsonify({
        'id': user.id,
        'screen_name': user.screen_name,
        'avatar_url': user.avatar_url,
    })


@blueprint.route('/me')
@login_required
@templated
def view_current():
    """Show the current user's internal profile."""
    current_user = g.current_user

    user = user_service.find_active_db_user(current_user.id)
    if user is None:
        abort(404)

    if get_site_mode().is_public():
        subscribed_to_newsletter = newsletter_service.is_subscribed(
            user.id, g.brand_id)
    else:
        subscribed_to_newsletter = None

    return {
        'user': user,
        'subscribed_to_newsletter': subscribed_to_newsletter,
    }


@blueprint.route('/me.json')
def view_current_as_json():
    """Show selected attributes of the current user's profile as JSON."""
    if get_site_mode().is_admin():
        abort(404)

    user = g.current_user

    if not user.is_active:
        # Return empty response.
        return Response(status=403)

    return jsonify({
        'id': user.id,
        'screen_name': user.screen_name,
        'avatar_url': user.avatar_url,
    })


@blueprint.route('/email_address_confirmations/request')
@templated
def request_email_address_confirmation_email_form(erroneous_form=None):
    """Show a form to request the email address confirmation email for the user
    account again.
    """
    form = erroneous_form if erroneous_form else RequestConfirmationEmailForm()
    return {'form': form}


@blueprint.route('/email_address_confirmations/request', methods=['POST'])
def request_email_address_confirmation_email():
    """Request the email address confirmation email for the user account
    again.
    """
    form = RequestConfirmationEmailForm(request.form)
    if not form.validate():
        return request_email_address_confirmation_email_form(form)

    screen_name = form.screen_name.data.strip()
    user = user_service.find_user_by_screen_name(screen_name)

    if user is None:
        flash_error('Der Benutzername "{}" ist unbekannt.', screen_name)
        return request_email_address_confirmation_email_form(form)

    if user.email_address_verified:
        flash_notice(
            'Die E-Mail-Adresse für den Benutzernamen "{}" wurde bereits '
            'bestätigt.',
            user.screen_name)
        return request_email_address_confirmation_email_form()

    verification_token = verification_token_service \
        .find_or_create_for_email_address_confirmation(user.id)
    email_address_confirmation_service.send_email_address_confirmation_email(
        user.email_address, user.screen_name, verification_token, g.brand_id)

    flash_success(
        'Der Link zur Bestätigung der für den Benutzernamen "{}" '
        'hinterlegten E-Mail-Adresse wurde erneut versendet.',
        user.screen_name)
    return request_email_address_confirmation_email_form()


@blueprint.route('/email_address_confirmations/<uuid:token>')
def confirm_email_address(token):
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


@blueprint.route('/me/details')
@templated
def details_update_form(erroneous_form=None):
    """Show a form to update the current user's details."""
    current_user = _get_current_user_or_404()
    user = user_service.find_user_with_details(current_user.id)

    form = erroneous_form if erroneous_form else DetailsForm(obj=user.detail)
    country_names = country_service.get_country_names()

    return {
        'form': form,
        'country_names': country_names,
    }


@blueprint.route('/me/details', methods=['POST'])
def details_update():
    """Update the current user's details."""
    current_user = _get_current_user_or_404()

    form = DetailsForm(request.form)

    if not form.validate():
        return details_update_form(form)

    first_names = form.first_names.data.strip()
    last_name = form.last_name.data.strip()
    date_of_birth = form.date_of_birth.data
    country = form.country.data.strip()
    zip_code = form.zip_code.data.strip()
    city = form.city.data.strip()
    street = form.street.data.strip()
    phone_number = form.phone_number.data.strip()

    user_command_service.update_user_details(current_user.id, first_names,
                                             last_name, date_of_birth, country,
                                             zip_code, city, street,
                                             phone_number)

    flash_success('Deine Daten wurden gespeichert.')
    return redirect_to('.view_current')


def _get_current_user_or_404():
    user = g.current_user
    if not user.is_active:
        abort(404)

    return user
