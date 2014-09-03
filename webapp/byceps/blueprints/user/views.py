# -*- coding: utf-8 -*-

"""
byceps.blueprints.user.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from datetime import datetime

from flask import abort, g, request, session, url_for

from ...config import get_site_mode, SiteMode
from ...database import db
from ...mail import mail
from ...util.framework import create_blueprint, flash_error, flash_success
from ...util.image import create_thumbnail, Dimensions, \
    guess_type as guess_image_type, read_dimensions
from ...util.templating import templated
from ...util import upload
from ...util.views import redirect_to, respond_no_content

from ..authorization.models import Role
from ..terms.models import Consent, ConsentContext

from .forms import AvatarImageUpdateForm, CreateForm, LoginForm
from .models import NewsletterSubscription, NewsletterSubscriptionState, User, \
    VerificationToken, VerificationTokenPurpose


MAXIMUM_AVATAR_IMAGE_DIMENSIONS = Dimensions(110, 150)


blueprint = create_blueprint('user', __name__)


@blueprint.before_app_request
def before_request():
    g.current_user = UserSession.get_user()


@blueprint.route('/<id>')
@templated
def view(id):
    """Show a user's profile."""
    user = find_user_by_id(id)
    return {'user': user}


@blueprint.route('/create')
@templated
def create_form(errorneous_form=None):
    """Show a form to create a user."""
    form = errorneous_form if errorneous_form else CreateForm()
    return {'form': form}


@blueprint.route('/', methods=['POST'])
def create():
    """Create a user."""
    form = CreateForm(request.form)
    if not form.validate():
        return create_form(form)

    screen_name = form.screen_name.data
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
    db.session.add(user)

    verification_token = VerificationToken(
        user, VerificationTokenPurpose.email_address_confirmation)
    db.session.add(verification_token)

    terms_consent = Consent(user, ConsentContext.account_creation)
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
        db.session.rollback()
        flash_error('Das Benutzerkonto für "{}" konnte nicht angelegt werden.',
                    user.screen_name)
        return create_form(form)

    db.session.commit()

    send_email_address_confirmation_email(user, verification_token)

    flash_success('Das Benutzerkonto für "{}" wurde angelegt.',
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


def send_email_address_confirmation_email(user, verification_token):
    confirmation_url = url_for('.confirm_email_address',
                               user_id=user.id,
                               token=verification_token.token,
                               _external=True)

    subject = 'Bestätigung deiner E-Mail-Adresse'.encode('utf-8')
    body = (
        'Hallo {0.screen_name},\n\n'
        'bitte bestätige deine E-Mail-Adresse indem du diese URL abrufst: {1}'
    ).format(user, confirmation_url).encode('utf-8')
    recipients = [user.email_address]

    mail.send_message(subject=subject, body=body, recipients=recipients)


@blueprint.route('/<user_id>/confirm_email_address/<token>')
def confirm_email_address(user_id, token):
    """Confirm the user's e-mail address."""
    user = find_user_by_id(user_id)
    verification_token = VerificationToken.find(
        token, user, VerificationTokenPurpose.email_address_confirmation)

    if verification_token is None:
        abort(404)

    user.enabled = True
    db.session.delete(verification_token)
    db.session.commit()

    flash_success(
        'Die E-Mail-Adresse wurde bestätigt. Das Benutzerkonto "{}" ist nun aktiv.',
        user.screen_name)
    return redirect_to('.login_form')


@blueprint.route('/me')
@templated
def view_current():
    user = get_current_user_or_404()
    return {'user': user}


@blueprint.route('/me/avatar/update')
@templated
def avatar_image_form():
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
def avatar_image():
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
    return redirect_to('.view', id=user.id)


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


@blueprint.route('/login')
@templated
def login_form():
    """Show login form."""
    logged_in = g.current_user.is_active()
    if logged_in:
        flash_error('Du bist bereits als Benutzer "{}" angemeldet.', g.current_user.screen_name)

    form = LoginForm()
    return {
        'logged_in': logged_in,
        'form': form,
    }


@blueprint.route('/login', methods=['POST'])
@respond_no_content
def login():
    """Allow the user to authenticate with e-mail address and password."""
    if g.current_user.is_active():
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

    if get_site_mode() == SiteMode.admin and not user.is_orga_for_any_brand:
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
    if not user.is_active():
        abort(404)

    return user


class UserSession(object):

    KEY = 'user_id'

    @classmethod
    def start(cls, user, *, permanent=False):
        """End the user's session by deleting the session cookie."""
        session[cls.KEY] = str(user.id)
        session.permanent = permanent

    @classmethod
    def end(cls):
        """End the user's session by deleting the session cookie."""
        session.pop(cls.KEY, None)
        session.permanent = False

    @classmethod
    def get_user(cls):
        """Return the current user, falling back to the anonymous user."""
        return User.load(cls.get_user_id())

    @classmethod
    def get_user_id(cls):
        """Return the current user's ID, or `None` if not available."""
        return session.get(cls.KEY)
