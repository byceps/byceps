# -*- coding: utf-8 -*-

"""
byceps.blueprints.user.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
"""

from datetime import datetime
from operator import attrgetter

from flask import abort, current_app, g, request, session, url_for

from ...config import get_site_mode, get_user_registration_enabled
from ...database import db
from ...mail import mail
from ...util.framework import create_blueprint, flash_error, flash_notice, \
    flash_success
from ...util.image import create_thumbnail, Dimensions, \
    guess_type as guess_image_type, read_dimensions
from ...util.templating import templated
from ...util import upload
from ...util.views import redirect_to, respond_no_content

from ..authorization.models import Role
from ..newsletter.models import Subscription as NewsletterSubscription, \
    SubscriptionState as NewsletterSubscriptionState
from ..terms import service as terms_service
from ..ticket.service import find_ticket_for_user, get_attended_parties
from ..verification_token import service as verification_token_service

from .forms import AvatarImageUpdateForm, DetailsForm, LoginForm, \
    RequestConfirmationEmailForm, RequestPasswordResetForm, \
    ResetPasswordForm, UpdatePasswordForm, UserCreateForm
from .models import User


MAXIMUM_AVATAR_IMAGE_DIMENSIONS = Dimensions(110, 150)


blueprint = create_blueprint('user', __name__)


@blueprint.before_app_request
def before_request():
    g.current_user = UserSession.get_user()


@blueprint.route('/<uuid:id>')
@templated
def view(id):
    """Show a user's profile."""
    user = find_user_by_id(id)
    current_party_ticket = find_ticket_for_user(user, g.party)
    attended_parties = get_attended_parties(user)
    attended_parties.sort(key=attrgetter('starts_at'), reverse=True)

    return {
        'user': user,
        'current_party_ticket': current_party_ticket,
        'attended_parties': attended_parties,
    }


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

    if is_screen_name_already_assigned(screen_name):
        flash_error(
            'Dieser Benutzername ist bereits einem Benutzerkonto zugeordnet.')
        return create_form(form)

    if is_email_address_already_assigned(email_address):
        flash_error(
            'Diese E-Mail-Adresse ist bereits einem Benutzerkonto zugeordnet.')
        return create_form(form)

    user = User.create(screen_name, email_address, password)
    user.detail.first_names = first_names
    user.detail.last_name = last_name
    db.session.add(user)

    verification_token = verification_token_service.build_for_email_address_confirmation(user)
    db.session.add(verification_token)

    terms_version = terms_service.get_current_version()
    terms_consent = terms_service.build_consent_on_account_creation(user, terms_version)
    db.session.add(terms_consent)

    newsletter_subscription_state = NewsletterSubscriptionState.requested \
        if subscribe_to_newsletter \
        else NewsletterSubscriptionState.declined
    newsletter_subscription = NewsletterSubscription(user, newsletter_subscription_state)
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

    send_email_address_confirmation_email(user, verification_token)

    flash_success(
        'Das Benutzerkonto für "{}" wurde angelegt. '
        'Bevor du dich damit anmelden kannst muss zunächst der Link in '
        'der an die angegebene Adresse verschickten E-Mail besucht werden.'
        ,
        user.screen_name)
    return redirect_to('.view', id=user.id)


def is_screen_name_already_assigned(screen_name):
    return do_users_matching_filter_exist(User.screen_name, screen_name)


def is_email_address_already_assigned(email_address):
    return do_users_matching_filter_exist(User.email_address, email_address)


def do_users_matching_filter_exist(model_attribute, search_value):
    """Return `True` if any users match the filter.

    Comparison is done case-insensitively.
    """
    user_count = User.query \
        .filter(db.func.lower(model_attribute) == search_value.lower()) \
        .count()
    return user_count > 0


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

    verification_token = verification_token_service.find_for_email_address_confirmation_by_user(user)
    if verification_token is None:
        verification_token = verification_token_service.build_for_email_address_confirmation(user)
        db.session.add(verification_token)
        db.session.commit()

    send_email_address_confirmation_email(user, verification_token)

    flash_success(
        'Der Link zur Bestätigung der für den Benutzernamen "{}" '
        'hinterlegten E-Mail-Adresse wurde erneut versendet.',
        user.screen_name)
    return request_email_address_confirmation_email_form()


def send_email_address_confirmation_email(user, verification_token):
    confirmation_url = url_for('.confirm_email_address',
                               token=verification_token.token,
                               _external=True)

    subject = '{0.screen_name}, bitte bestätige deine E-Mail-Adresse'.format(user)
    body = (
        'Hallo {0.screen_name},\n\n'
        'bitte bestätige deine E-Mail-Adresse indem du diese URL abrufst: {1}'
    ).format(user, confirmation_url)
    recipients = [user.email_address]

    mail.send_message(subject=subject, body=body, recipients=recipients)


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
    return redirect_to('.login_form')


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

    send_password_reset_email(user, verification_token)

    flash_success(
        'Ein Link zum Setzen eines neuen Passworts für den Benutzernamen "{}" '
        'wurde an die hinterlegte E-Mail-Adresse versendet.',
        user.screen_name)
    return request_password_reset_form()


def send_password_reset_email(user, verification_token):
    confirmation_url = url_for('.password_reset_form',
                               token=verification_token.token,
                               _external=True)

    subject = '{0.screen_name}, so kannst du ein neues Passwort festlegen'.format(user)
    body = (
        'Hallo {0.screen_name},\n\n'
        'du kannst ein neues Passwort festlegen indem du diese URL abrufst: {1}'
    ).format(user, confirmation_url)
    recipients = [user.email_address]

    mail.send_message(subject=subject, body=body, recipients=recipients)


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
    return redirect_to('.login_form')


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


@blueprint.route('/me')
@templated
def view_current():
    user = get_current_user_or_404()
    newsletter_subscription_state = NewsletterSubscription.get_state_for_user(user)
    return {
        'user': user,
        'newsletter_subscription_state': newsletter_subscription_state,
        'NewsletterSubscriptionState': NewsletterSubscriptionState,
    }


@blueprint.route('/me/details')
@templated
def details_update_form(erroneous_form=None):
    """Show a form to update the current user's details."""
    user = get_current_user_or_404()
    form = erroneous_form if erroneous_form else DetailsForm(obj=user.detail)
    return {'form': form}


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
    user.detail.zip_code = form.zip_code.data.strip()
    user.detail.city = form.city.data.strip()
    user.detail.street = form.street.data.strip()
    user.detail.phone_number = form.phone_number.data.strip()
    db.session.commit()

    flash_success('Deine Daten wurden gespeichert.')
    return redirect_to('.view_current')


@blueprint.route('/me/avatar/update')
@templated
def avatar_image_update_form():
    """Show a form to update the current user's avatar image."""
    get_current_user_or_404()
    form = AvatarImageUpdateForm()
    return {
        'form': form,
    }


# Route to generate avatar image URLs.
blueprint.add_url_rule(
    '/avatars/<filename>',
    endpoint='avatar_image',
    methods=['GET'],
    build_only=True)


@blueprint.route('/me/avatar', methods=['POST'])
def avatar_image_update():
    """Update the current user's avatar image."""
    user = get_current_user_or_404()

    form = AvatarImageUpdateForm(request.form)

    image = request.files.get('image')
    if not image or not image.filename:
        abort(400, 'No file to upload has been specified.')

    stream = image.stream

    image_type = determine_image_type(stream)
    user.set_avatar_image(datetime.now(), image_type)

    if is_image_too_large(stream):
        stream = create_thumbnail(
            stream, image_type.name, MAXIMUM_AVATAR_IMAGE_DIMENSIONS)

    try:
        upload.store(stream, user.avatar_image_path)
    except FileExistsError:
        # Werkzeug implements no default response for code 409.
        ##abort(409, 'File already exists, not overwriting.')
        abort(500, 'File already exists, not overwriting.')

    db.session.commit()

    flash_success('Das Avatarbild wurde aktualisiert.', icon='upload')
    return redirect_to('.view_current')


def determine_image_type(stream):
    image_type = guess_image_type(stream)
    if image_type is None:
        abort(400, 'Only GIF, JPEG and PNG images are allowed.')

    stream.seek(0)
    return image_type


def is_image_too_large(stream):
    actual_dimensions = read_dimensions(stream)
    stream.seek(0)
    return actual_dimensions > MAXIMUM_AVATAR_IMAGE_DIMENSIONS


@blueprint.route('/me/avatar', methods=['DELETE'])
@respond_no_content
def delete_avatar_image():
    """Remove the current user's avatar image."""
    user = get_current_user_or_404()

    user.remove_avatar_image()
    db.session.commit()

    flash_success('Das Avatarbild wurde entfernt.')
    return [('Location', url_for('.view_current'))]


@blueprint.route('/login')
@templated
def login_form():
    """Show login form."""
    logged_in = g.current_user.is_active
    if logged_in:
        flash_error('Du bist bereits als Benutzer "{}" angemeldet.', g.current_user.screen_name)

    form = LoginForm()
    user_registration_enabled = get_user_registration_enabled()
    return {
        'logged_in': logged_in,
        'form': form,
        'user_registration_enabled': user_registration_enabled,
    }


@blueprint.route('/login', methods=['POST'])
@respond_no_content
def login():
    """Allow the user to authenticate with e-mail address and password."""
    if g.current_user.is_active:
        return

    form = LoginForm(request.form)

    screen_name = form.screen_name.data
    password = form.password.data
    permanent = form.permanent.data
    if not all([screen_name, password]):
        abort(403)

    # Verify credentials.
    user = User.authenticate(screen_name, password)
    if user is None:
        # Authentication failed.
        abort(403)

    if get_site_mode().is_admin() and not user.is_orga_for_any_brand:
        # Authenticated user must be an orga to be allowed to enter the
        # admin area but isn't.
        abort(403)

    # Authorization succeeded.
    UserSession.start(user, permanent=permanent)
    flash_success('Erfolgreich eingeloggt als {}.', user.screen_name)


@blueprint.route('/logout', methods=['POST'])
@respond_no_content
def logout():
    """Log out user by deleting the corresponding cookie."""
    UserSession.end()
    flash_success('Erfolgreich ausgeloggt.')


def find_user_by_id(id):
    return User.query.get_or_404(id)


def get_current_user_or_404():
    user = g.current_user
    if not user.is_active:
        abort(404)

    return user


class UserSession(object):

    KEY_USER_ID = 'user_id'
    KEY_USER_AUTH_TOKEN = 'user_auth_token'

    @classmethod
    def start(cls, user, *, permanent=False):
        """Initialize the user's session by putting the relevant data
        into the session cookie.
        """
        session[cls.KEY_USER_ID] = str(user.id)
        session[cls.KEY_USER_AUTH_TOKEN] = str(user.auth_token)
        session.permanent = permanent

    @classmethod
    def end(cls):
        """End the user's session by deleting the session cookie."""
        session.pop(cls.KEY_USER_ID, None)
        session.pop(cls.KEY_USER_AUTH_TOKEN, None)
        session.permanent = False

    @classmethod
    def get_user(cls):
        """Return the current user, falling back to the anonymous user."""
        return User.load(cls.get_user_id(), cls.get_auth_token())

    @classmethod
    def get_user_id(cls):
        """Return the current user's ID, or `None` if not available."""
        return session.get(cls.KEY_USER_ID)

    @classmethod
    def get_auth_token(cls):
        """Return the current user's auth token, or `None` if not available."""
        return session.get(cls.KEY_USER_AUTH_TOKEN)
