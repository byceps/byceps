"""
tests.helpers
~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from contextlib import contextmanager

from flask import appcontext_pushed, g

from byceps.application import create_app
from byceps.database import db
from byceps.services.authentication.session import service as session_service
from byceps.services.authorization import service as authorization_service
from byceps.services.party import service as party_service
from byceps.services.site import service as site_service

from testfixtures.brand import create_brand as _create_brand
from testfixtures.party import create_party as _create_party
from testfixtures.user import create_user as _create_user, \
    create_user_with_detail as _create_user_with_detail

from .base import CONFIG_FILENAME_TEST_PARTY


@contextmanager
def app_context(*, config_filename=CONFIG_FILENAME_TEST_PARTY):
    app = create_app(config_filename)

    with app.app_context():
        yield app


@contextmanager
def current_party_set(app, party):
    def handler(sender, **kwargs):
        g.party_id = party.id
        g.brand_id = party.brand_id

    with appcontext_pushed.connected_to(handler, app):
        yield


@contextmanager
def current_user_set(app, user):
    def handler(sender, **kwargs):
        g.current_user = user

    with appcontext_pushed.connected_to(handler, app):
        yield


def create_user(*args, **kwargs):
    user = _create_user(*args, **kwargs)

    db.session.add(user)
    db.session.commit()

    return user


def create_user_with_detail(*args, **kwargs):
    user = _create_user_with_detail(*args, **kwargs)

    db.session.add(user)
    db.session.commit()

    return user


def assign_permissions_to_user(user_id, role_id, permission_ids,
                               *, initiator_id=None):
    """Create the role and permissions, assign the permissions to the
    role, and assign the role to the user.
    """
    role = authorization_service.create_role(role_id, role_id)

    for permission_id in permission_ids:
        permission = authorization_service.create_permission(permission_id,
                                                             permission_id)
        authorization_service.assign_permission_to_role(permission.id, role.id)

    authorization_service.assign_role_to_user(user_id, role.id,
                                              initiator_id=initiator_id)


def create_brand(brand_id='acmecon', title='ACME Entertainment Convention'):
    brand = _create_brand(id=brand_id, title=title)

    db.session.add(brand)
    db.session.commit()

    return brand


def create_party(brand_id, party_id='acmecon-2014', title='ACMECon 2014'):
    party = _create_party(id=party_id, title=title, brand_id=brand_id)

    db.session.add(party)
    db.session.commit()

    return party_service._db_entity_to_party(party)


def create_site(party_id, *, site_id='acmecon-2014-website', title='Website',
                server_name='www.example.com'):
    return site_service.create_site(site_id, party_id, title, server_name)


@contextmanager
def http_client(app, *, user_id=None):
    """Provide an HTTP client.

    If a user ID is given, the client authenticates with the user's
    credentials.
    """
    client = app.test_client()

    if user_id is not None:
        _add_user_credentials_to_session(client, user_id)

    yield client


def _add_user_credentials_to_session(client, user_id):
    session_token = session_service.find_session_token_for_user(user_id)

    with client.session_transaction() as session:
        session['user_id'] = str(user_id)
        session['user_auth_token'] = str(session_token.token)


def login_user(user_id):
    """Authenticate the user to create a session."""
    session_service.get_session_token(user_id)
