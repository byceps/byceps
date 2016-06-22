# -*- coding: utf-8 -*-

"""
byceps.blueprints.user.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from operator import attrgetter

from flask import abort, current_app, g, jsonify, request, Response, url_for

from ...config import get_site_mode, get_user_registration_enabled
from ...database import db
from ...services import countries as countries_service
from ...util.framework import create_blueprint, flash_error, flash_notice, \
    flash_success
from ...util.templating import templated
from ...util.views import redirect_to, respond_no_content

from ..authorization.models import Role
from ..newsletter.models import Subscription as NewsletterSubscription, \
    SubscriptionState as NewsletterSubscriptionState
from ..newsletter import service as newsletter_service
from ..orga import service as orga_service
from ..terms import service as terms_service
from ..ticket import service as ticket_service
from ..verification_token import service as verification_token_service

from .forms import DetailsForm, RequestConfirmationEmailForm, \
    RequestPasswordResetForm, ResetPasswordForm, UpdatePasswordForm, \
    UserCreateForm
from .models.user import User
from . import service
from . import signals


blueprint = create_blueprint('user', __name__)


@blueprint.route('/<uuid:id>')
@templated
def view(id):
    """Show a user's profile."""
    if get_site_mode().is_admin():
        abort(404)

    user = find_user_by_id(id)

    if user.deleted:
        abort(410, 'User account has been deleted.')

    orga_team_membership = orga_service.find_orga_team_membership_for_party(user, g.party)

    current_party_tickets = ticket_service.find_tickets_used_by_user(user, g.party)

    attended_parties = ticket_service.get_attended_parties(user)
    attended_parties.sort(key=attrgetter('starts_at'), reverse=True)

    return {
        'user': user,
        'orga_team_membership': orga_team_membership,
        'current_party_tickets': current_party_tickets,
        'attended_parties': attended_parties,
    }


@blueprint.route('/<uuid:id>.json')
def view_as_json(id):
    """Show selected attributes of a user's profile as JSON."""
    if get_site_mode().is_admin():
        abort(404)

    user = User.query.get(id)

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
        newsletter_subscription_state = newsletter_service \
            .get_subscription_state(user, g.party.brand)
    else:
        newsletter_subscription_state = None

    return {
        'user': user,
        'newsletter_subscription_state': newsletter_subscription_state,
        'NewsletterSubscriptionState': NewsletterSubscriptionState,
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

    user = User.create(screen_name, email_address, password)
    user.detail.first_names = first_names
    user.detail.last_name = last_name
    db.session.add(user)

    verification_token = verification_token_service.build_for_email_address_confirmation(user)
    db.session.add(verification_token)

    terms_version = terms_service.get_current_version(g.party.brand)
    terms_consent = terms_service.build_consent_on_account_creation(user, terms_version)
    db.session.add(terms_consent)

    newsletter_subscription_state = NewsletterSubscriptionState.requested \
        if subscribe_to_newsletter \
        else NewsletterSubscriptionState.declined
    newsletter_subscription = NewsletterSubscription(user, g.party.brand,
                                                     newsletter_subscription_state)
    db.session.add(newsletter_subscription)

    board_user_role = Role.query.get('board_user')
    user.roles.add(board_user_role)

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error('User creation failed: %s', e)
        db.session.rollback()
        flash_error('Das Benutzerkonto für "{}" konnte nicht angelegt werden.',
                    user.screen_name)
        return create_form(form)

    service.send_email_address_confirmation_email(user, verification_token)

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
    user = User.query.filter_by(screen_name=screen_name).first()

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
    user.enabled = True
    db.session.delete(verification_token)
    db.session.commit()

    flash_success(
        'Die E-Mail-Adresse wurde bestätigt. Das Benutzerkonto "{}" ist nun aktiviert.',
        user.screen_name)
    signals.email_address_confirmed.send(None, user=user)

    return redirect_to('authentication.login_form')


@blueprint.route('/me/password/reset/request')
@templated
def request_password_reset_form(erroneous_form=None):
    """Show a form to request a password reset."""
    form = erroneous_form if erroneous_form else RequestPasswordResetForm()
    return {'form': form}


@blueprint.route('/me/password/reset/request', methods=['POST'])
def request_password_reset():
    """Request a password reset."""
    form = RequestPasswordResetForm(request.form)
    if not form.validate():
        return request_password_reset_form(form)

    screen_name = form.screen_name.data.strip()
    user = User.query.filter_by(screen_name=screen_name).first()

    if user is None:
        flash_error('Der Benutzername "{}" ist unbekannt.', screen_name)
        return request_password_reset_form(form)

    if not user.enabled:
        flash_error('Die E-Mail-Adresse für das Benutzerkonto "{}" wurde '
                    'noch nicht bestätigt.', screen_name)
        return redirect_to('.request_email_address_confirmation_email')

    verification_token = verification_token_service.build_for_password_reset(user)
    db.session.add(verification_token)
    db.session.commit()

    service.send_password_reset_email(user, verification_token)

    flash_success(
        'Ein Link zum Setzen eines neuen Passworts für den Benutzernamen "{}" '
        'wurde an die hinterlegte E-Mail-Adresse versendet.',
        user.screen_name)
    return request_password_reset_form()


@blueprint.route('/me/password/reset/token/<uuid:token>')
@templated
def password_reset_form(token, erroneous_form=None):
    """Show a form to reset the current user's password."""
    verification_token = verification_token_service.find_for_password_reset_by_token(token)
    _verify_password_reset_token(verification_token)

    form = erroneous_form if erroneous_form else ResetPasswordForm()
    return {
        'form': form,
        'token': token,
    }


@blueprint.route('/me/password/reset/token/<uuid:token>', methods=['POST'])
def password_reset(token):
    """Reset the current user's password."""
    verification_token = verification_token_service.find_for_password_reset_by_token(token)
    _verify_password_reset_token(verification_token)

    form = ResetPasswordForm(request.form)
    if not form.validate():
        return password_reset_form(token, form)

    user = verification_token.user
    user.set_password(form.new_password.data)
    user.set_new_auth_token()
    db.session.delete(verification_token)
    db.session.commit()

    flash_success('Das Passwort wurde geändert.')
    return redirect_to('authentication.login_form')


def _verify_password_reset_token(verification_token ):
    if verification_token is None or verification_token.is_expired:
        flash_error('Es wurde kein gültiges Token angegeben. '
                    'Ein Token ist nur 24 Stunden lang gültig.')
        abort(404)


@blueprint.route('/me/password/update')
@templated
def password_update_form(erroneous_form=None):
    """Show a form to update the current user's password."""
    user = get_current_user_or_404()
    form = erroneous_form if erroneous_form else UpdatePasswordForm()
    return {'form': form}


@blueprint.route('/me/password', methods=['POST'])
def password_update():
    """Update the current user's password."""
    user = get_current_user_or_404()
    form = UpdatePasswordForm(request.form)

    if not form.validate():
        return password_update_form(form)

    user.set_password(form.new_password.data)
    user.set_new_auth_token()
    db.session.commit()

    flash_success('Das Passwort wurde geändert.')
    return redirect_to('.view_current')


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

    user.detail.first_names = form.first_names.data.strip()
    user.detail.last_name = form.last_name.data.strip()
    user.detail.date_of_birth = form.date_of_birth.data
    user.detail.country = form.country.data.strip()
    user.detail.zip_code = form.zip_code.data.strip()
    user.detail.city = form.city.data.strip()
    user.detail.street = form.street.data.strip()
    user.detail.phone_number = form.phone_number.data.strip()
    db.session.commit()

    flash_success('Deine Daten wurden gespeichert.')
    return redirect_to('.view_current')


def find_user_by_id(id):
    return User.query.get_or_404(id)


def get_current_user_or_404():
    user = g.current_user
    if not user.is_active:
        abort(404)

    return user
