# -*- coding: utf-8 -*-

"""
byceps.blueprints.user.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from datetime import datetime
from uuid import UUID

from flask import abort, g, redirect, request, session, url_for
from werkzeug.security import check_password_hash

from ...database import db
from ...util.framework import create_blueprint, flash_error, flash_success
from ...util.templating import templated
from ...util.views import respond_no_content

from .forms import CreateForm, LoginForm
from .models import GUEST_USER_ID, User



SESSION_KEY_USER_ID = 'user_id'


blueprint = create_blueprint('user', __name__)


@blueprint.before_app_request
def before_request():
    g.current_user = determine_current_user()


@blueprint.route('/')
@templated
def index():
    """List users."""
    users = User.query.all()
    return {'users': users}


@blueprint.route('/<id>')
@templated
def view(id):
    """Show a user's profile."""
    try:
        uuid = UUID(id)
    except ValueError:
        abort(404)
    user = User.query.get_or_404(uuid)
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

    name = form.name.data
    email_address = form.email_address.data
    password = form.password.data

    user = User.create(name, email_address, password)
    db.session.add(user)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash_error('Das Benutzerkonto für "{}" konnte nicht angelegt werden.',
                    user.name)
        return create_form(form)

    flash_success('Das Benutzerkonto für "{}" wurde angelegt.', user.name)
    return redirect(url_for('.view', id=user.id))


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

    name = form.name.data
    password = form.password.data
    if not all([name, password]):
        abort(403)

    # Verify credentials.
    user = User.query.filter_by(name=name).first()
    if not is_user_authorized(user, password):
        # Authentication failed.
        abort(403)

    # Authorization succeeded.
    update_session_as_logged_in(user)
    flash_success('Erfolgreich eingeloggt als {}.', user.name)


@blueprint.route('/logout', methods=['POST'])
@respond_no_content
def logout():
    """Log out user by deleting the corresponding cookie."""
    update_session_as_logged_out()
    flash_success('Erfolgreich ausgeloggt.')


def determine_current_user():
    """Retrieve the current user, falling back to the anonymous user."""
    user_id = get_user_id_from_session()
    return User.load(user_id)


def get_user_id_from_session():
    user_id = session.get(SESSION_KEY_USER_ID)
    if user_id is not None:
        try:
            return UUID(user_id)
        except ValueError:
            pass


def is_user_authorized(user, password):
    if user is None:
        # Unknown user name.
        return False

    if not check_password_hash(user.password_hash, password):
        # Invalid password.
        return False

    if not user.is_active():
        # User is disabled.
        return False

    return True


def update_session_as_logged_in(user):
    session[SESSION_KEY_USER_ID] = str(user.id)
    session.permanent = True


def update_session_as_logged_out():
    """Delete the session cookie."""
    session.pop(SESSION_KEY_USER_ID, None)
    session.permanent = False
