# -*- coding: utf-8 -*-

"""
byceps.blueprints.user.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from datetime import datetime

from flask import abort, g, request, session

from ...database import db
from ...util.framework import create_blueprint, flash_error, flash_success
from ...util.image import Dimensions, guess_type as guess_image_type, \
    read_dimensions
from ...util.templating import templated
from ...util import upload
from ...util.views import redirect_to, respond_no_content

from ..terms.models import Consent, ConsentContext

from .forms import AvatarImageUpdateForm, CreateForm, LoginForm
from .models import User


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
    email_address = form.email_address.data
    password = form.password.data
    consent_to_terms = form.consent_to_terms.data

    user = User.create(screen_name, email_address, password)
    db.session.add(user)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash_error('Das Benutzerkonto für "{}" konnte nicht angelegt werden.',
                    user.screen_name)
        return create_form(form)

    Consent.create(user, ConsentContext.account_creation)

    flash_success('Das Benutzerkonto für "{}" wurde angelegt.',
                  user.screen_name)
    return redirect_to('.view', id=user.id)


@blueprint.route('/<id>/avatar/update')
@templated
def avatar_image_form(id):
    user = find_user_by_id(id)
    form = AvatarImageUpdateForm()
    return {
        'user': user,
        'form': form,
    }


# Route to generate avatar image URLs.
blueprint.add_url_rule(
    '/avatars/<filename>',
    endpoint='avatar_image',
    methods=['GET'],
    build_only=True)


@blueprint.route('/<id>/avatar', methods=['POST'])
def avatar_image(id):
    user = find_user_by_id(id)

    form = AvatarImageUpdateForm(request.form)

    image = request.files.get('image')
    if not image or not image.filename:
        abort(400, 'No file to upload has been specified.')

    image_type = determine_image_type(image)
    user.set_avatar_image(datetime.now(), image_type)

    ensure_dimensions(image)

    try:
        upload.store(image.stream, user.avatar_image_path)
    except FileExistsError:
        # Werkzeug implements no default response for code 409.
        ##abort(409, 'File already exists, not overwriting.')
        abort(500, 'File already exists, not overwriting.')

    db.session.commit()

    return redirect_to('.view', id=user.id)


def determine_image_type(image):
    image_type = guess_image_type(image.stream)
    if image_type is None:
        abort(400, 'Only GIF, JPEG and PNG images are allowed.')

    image.stream.seek(0)
    return image_type


def ensure_dimensions(image):
    required_dimensions = Dimensions(110, 150)
    actual_dimensions = read_dimensions(image.stream)
    image.stream.seek(0)
    if actual_dimensions != required_dimensions:
        abort(400,
              'Image width and height must be exactly {0.width:d} x {0.height:d} pixels.'
              .format(required_dimensions))


@blueprint.route('/login')
@templated
def login_form():
    """Show login form."""
    form = LoginForm()
    return {'form': form}


@blueprint.route('/login', methods=['POST'])
@respond_no_content
def login():
    """Allow the user to authenticate with e-mail address and password."""
    if g.current_user.is_active():
        return

    form = LoginForm(request.form)

    screen_name = form.screen_name.data
    password = form.password.data
    if not all([screen_name, password]):
        abort(403)

    # Verify credentials.
    user = User.authenticate(screen_name, password)
    if user is None:
        # Authentication failed.
        abort(403)

    # Authorization succeeded.
    UserSession.start(user)
    flash_success('Erfolgreich eingeloggt als {}.', user.screen_name)


@blueprint.route('/logout', methods=['POST'])
@respond_no_content
def logout():
    """Log out user by deleting the corresponding cookie."""
    UserSession.end()
    flash_success('Erfolgreich ausgeloggt.')


def find_user_by_id(id):
    return User.query.get_or_404(id)


class UserSession(object):

    KEY = 'user_id'

    @classmethod
    def start(cls, user):
        """End the user's session by deleting the session cookie."""
        session[cls.KEY] = str(user.id)
        session.permanent = True

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
