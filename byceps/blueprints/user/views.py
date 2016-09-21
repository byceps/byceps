# -*- coding: utf-8 -*-

"""
byceps.blueprints.user.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from operator import attrgetter

from flask import abort, g, jsonify, request, Response

from ...config import get_site_mode, get_user_registration_enabled
from ...services.countries import service as countries_service
from ...services.user_badge import service as badge_service
from ...util.framework import create_blueprint, flash_error, flash_notice, \
    flash_success
from ...util.templating import templated
from ...util.views import redirect_to

from ..newsletter import service as newsletter_service
from ..orga import service as orga_service
from ..ticket import service as ticket_service
from ..verification_token import service as verification_token_service

from .forms import DetailsForm, RequestConfirmationEmailForm, UserCreateForm
from . import service
from . import signals


blueprint = create_blueprint('user', __name__)


@blueprint.route('/<uuid:id>')
@templated
def view(id):
    """Show a user's profile."""
    if get_site_mode().is_admin():
        abort(404)

    user = service.find_user(id)
    if user is None:
        abort(404)

    if user.deleted:
        abort(410, 'User account has been deleted.')

    badges = badge_service.get_badges_for_user(user.id)

    orga_team_membership = orga_service.find_orga_team_membership_for_party(user, g.party)

    current_party_tickets = ticket_service.find_tickets_used_by_user(user, g.party)

    attended_parties = ticket_service.get_attended_parties(user)
    attended_parties.sort(key=attrgetter('starts_at'), reverse=True)

    return {
        'user': user,
        'badges': badges,
        'orga_team_membership': orga_team_membership,
        'current_party_tickets': current_party_tickets,
        'attended_parties': attended_parties,
    }


@blueprint.route('/<uuid:id>.json')
def view_as_json(id):
    """Show selected attributes of a user's profile as JSON."""
    if get_site_mode().is_admin():
        abort(404)

    user = service.find_user(id)

    if not user:
        return _empty_json_response(404)

    if user.deleted:
        return _empty_json_response(410)

    return jsonify({
        'id': user.id,
        'screen_name': user.screen_name,
    })


@blueprint.route('/me')
@templated
def view_current():
    """Show the current user's internal profile."""
    user = get_current_user_or_404()

    if get_site_mode().is_public():
        brand_id = g.party.brand.id
        subscribed_to_newsletter = newsletter_service.is_subscribed(user.id,
                                                                    brand_id)
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
        return _empty_json_response(404)

    return jsonify({
        'id': user.id,
        'screen_name': user.screen_name,
    })


def _empty_json_response(status):
    return Response('{}', status=status, mimetype='application/json')


@blueprint.route('/create')
@templated
def create_form(erroneous_form=None):
    """Show a form to create a user."""
    if not get_user_registration_enabled():
        flash_error('Das Erstellen von Benutzerkonten ist deaktiviert.')
        abort(403)

    form = erroneous_form if erroneous_form else UserCreateForm()
    return {'form': form}


@blueprint.route('/', methods=['POST'])
def create():
    """Create a user."""
    if not get_user_registration_enabled():
        flash_error('Das Erstellen von Benutzerkonten ist deaktiviert.')
        abort(403)

    form = UserCreateForm(request.form)
    if not form.validate():
        return create_form(form)

    screen_name = form.screen_name.data.strip()
    first_names = form.first_names.data.strip()
    last_name = form.last_name.data.strip()
    email_address = form.email_address.data.lower()
    password = form.password.data
    consent_to_terms = form.consent_to_terms.data
    subscribe_to_newsletter = form.subscribe_to_newsletter.data

    if service.is_screen_name_already_assigned(screen_name):
        flash_error(
            'Dieser Benutzername ist bereits einem Benutzerkonto zugeordnet.')
        return create_form(form)

    if service.is_email_address_already_assigned(email_address):
        flash_error(
            'Diese E-Mail-Adresse ist bereits einem Benutzerkonto zugeordnet.')
        return create_form(form)

    try:
        user = service.create_user(screen_name, email_address, password,
                                   first_names, last_name, g.party.brand,
                                   subscribe_to_newsletter)
    except service.UserCreationFailed:
        flash_error('Das Benutzerkonto für "{}" konnte nicht angelegt werden.',
                    screen_name)
        return create_form(form)

    flash_success(
        'Das Benutzerkonto für "{}" wurde angelegt. '
        'Bevor du dich damit anmelden kannst muss zunächst der Link in '
        'der an die angegebene Adresse verschickten E-Mail besucht werden.'
        ,
        user.screen_name)
    signals.user_created.send(None, user=user)

    return redirect_to('.view', id=user.id)


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
    user = service.find_user_by_screen_name(screen_name)

    if user is None:
        flash_error('Der Benutzername "{}" ist unbekannt.', screen_name)
        return request_email_address_confirmation_email_form(form)

    if user.enabled:
        flash_notice(
            'Das Benutzerkonto mit dem Namen "{}" ist bereits aktiviert und '
            'muss nicht mehr bestätigt werden.',
            user.screen_name)
        return request_email_address_confirmation_email_form()

    verification_token = verification_token_service \
        .find_or_create_for_email_address_confirmation(user)
    service.send_email_address_confirmation_email(user, verification_token)

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
    verification_token = verification_token_service.find_for_email_address_confirmation_by_token(token)
    if verification_token is None:
        abort(404)

    user = verification_token.user

    service.confirm_email_address(verification_token)

    flash_success(
        'Die E-Mail-Adresse wurde bestätigt. Das Benutzerkonto "{}" ist nun aktiviert.',
        user.screen_name)
    signals.email_address_confirmed.send(None, user=user)

    return redirect_to('authentication.login_form')


@blueprint.route('/me/details')
@templated
def details_update_form(erroneous_form=None):
    """Show a form to update the current user's details."""
    user = get_current_user_or_404()

    form = erroneous_form if erroneous_form else DetailsForm(obj=user.detail)
    country_names = countries_service.get_country_names()

    return {
        'form': form,
        'country_names': country_names,
    }


@blueprint.route('/me/details', methods=['POST'])
def details_update():
    """Update the current user's details."""
    user = get_current_user_or_404()
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

    service.update_user_details(user, first_names, last_name, date_of_birth,
                                country, zip_code, city, street, phone_number)

    flash_success('Deine Daten wurden gespeichert.')
    return redirect_to('.view_current')


def get_current_user_or_404():
    user = g.current_user
    if not user.is_active:
        abort(404)

    return user
