"""
tests.helpers
~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from contextlib import contextmanager
from datetime import date, datetime
from pathlib import Path
from secrets import token_hex
from typing import Any, Optional

from flask import appcontext_pushed, g

from byceps.application import create_app
from byceps.database import db, generate_uuid
from byceps.services.authentication.session.models.current_user import (
    CurrentUser,
)
from byceps.services.authentication.session import service as session_service
from byceps.services.authorization import service as authz_service
from byceps.services.party import service as party_service
from byceps.services.site import service as site_service
from byceps.services.user import creation_service as user_creation_service
from byceps.services.user.creation_service import UserCreationFailed
from byceps.services.user.dbmodels.detail import UserDetail as DbUserDetail
from byceps.services.user.dbmodels.user import User as DbUser


_CONFIG_PATH = Path('../config')
CONFIG_FILENAME_TEST_SITE = _CONFIG_PATH / 'test_site.py'
CONFIG_FILENAME_TEST_ADMIN = _CONFIG_PATH / 'test_admin.py'


def create_admin_app(config_overrides: Optional[dict[str, Any]] = None):
    app = create_app(
        config_filename=CONFIG_FILENAME_TEST_ADMIN,
        config_overrides=config_overrides,
    )
    return app


def create_site_app(config_overrides: Optional[dict[str, Any]] = None):
    app = create_app(
        config_filename=CONFIG_FILENAME_TEST_SITE,
        config_overrides=config_overrides,
    )
    return app


def generate_token() -> str:
    return token_hex(4)


@contextmanager
def app_context(*, config_filename=CONFIG_FILENAME_TEST_SITE):
    app = create_app(config_filename=config_filename)

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
def current_user_set(app, current_user: CurrentUser):
    def handler(sender, **kwargs):
        g.user = current_user

    with appcontext_pushed.connected_to(handler, app):
        yield


def create_user(
    screen_name='Faith',
    *,
    user_id=None,
    created_at=None,
    email_address=None,
    email_address_verified=False,
    initialized=True,
    suspended=False,
    deleted=False,
    legacy_id=None,
    _commit=True,
) -> DbUser:
    if not user_id:
        user_id = generate_uuid()

    if not created_at:
        created_at = datetime.utcnow()

    if not email_address:
        email_address = f'user{user_id}@users.test'

    user = user_creation_service.build_user(
        created_at, screen_name, email_address
    )

    user.id = user_id
    user.email_address_verified = email_address_verified
    user.initialized = initialized
    user.suspended = suspended
    user.deleted = deleted
    user.legacy_id = legacy_id

    if _commit:
        db.session.add(user)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise UserCreationFailed(e)

    return user


DEFAULT_DATE_OF_BIRTH = date(1993, 2, 15)


def create_user_with_detail(
    screen_name='Faith',
    *,
    user_id=None,
    email_address=None,
    initialized=True,
    suspended=False,
    deleted=False,
    legacy_id=None,
    first_names='John Joseph',
    last_name='Doe',
    date_of_birth=DEFAULT_DATE_OF_BIRTH,
    country='State of Mind',
    zip_code='31337',
    city='Atrocity',
    street='Elite Street 1337',
    phone_number='555-CALL-ME-MAYBE',
) -> DbUser:
    user = create_user(
        screen_name,
        user_id=user_id,
        email_address=email_address,
        initialized=initialized,
        suspended=suspended,
        deleted=deleted,
        legacy_id=legacy_id,
        _commit=False,
    )

    detail = DbUserDetail(user=user)

    detail.first_names = first_names
    detail.last_name = last_name
    detail.date_of_birth = date_of_birth
    detail.country = country
    detail.zip_code = zip_code
    detail.city = city
    detail.street = street
    detail.phone_number = phone_number

    db.session.add(user)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise UserCreationFailed(e)

    return user


def create_permissions(permission_ids):
    for permission_id in permission_ids:
        authz_service.create_permission(
            permission_id, permission_id, ignore_if_exists=True
        )


def create_role_with_permissions_assigned(role_id, permission_ids):
    role = authz_service.create_role(role_id, role_id, ignore_if_exists=True)

    for permission_id in permission_ids:
        authz_service.assign_permission_to_role(permission_id, role_id)


def create_party(brand_id, party_id='acmecon-2014', title='ACMECon 2014'):
    starts_at = datetime(2014, 10, 24, 16, 0)
    ends_at = datetime(2014, 10, 26, 13, 0)

    return party_service.create_party(
        party_id, brand_id, title, starts_at, ends_at
    )


def create_site(
    site_id,
    brand_id,
    *,
    title=None,
    server_name=None,
    enabled=True,
    user_account_creation_enabled=True,
    login_enabled=True,
    party_id=None,
    news_channel_id=None,
    board_id=None,
    storefront_id=None,
):
    if title is None:
        title = site_id

    if server_name is None:
        server_name = f'{site_id}.test'

    return site_service.create_site(
        site_id,
        title,
        server_name,
        brand_id,
        enabled=enabled,
        user_account_creation_enabled=user_account_creation_enabled,
        login_enabled=login_enabled,
        party_id=party_id,
        news_channel_id=news_channel_id,
        board_id=board_id,
        storefront_id=storefront_id,
    )


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
