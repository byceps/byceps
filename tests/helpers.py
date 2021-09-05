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
from typing import Any, Iterable, Optional, Union

from flask import appcontext_pushed, Flask, g

from byceps.application import create_app
from byceps.database import db, generate_uuid
from byceps.services.authentication.password import service as password_service
from byceps.services.authentication.session.models.current_user import (
    CurrentUser,
)
from byceps.services.authentication.session import service as session_service
from byceps.services.authorization import service as authz_service
from byceps.services.authorization.transfer.models import PermissionID, RoleID
from byceps.services.board.transfer.models import BoardID
from byceps.services.party import service as party_service
from byceps.services.party.transfer.models import Party
from byceps.services.shop.storefront.transfer.models import StorefrontID
from byceps.services.site import service as site_service
from byceps.services.site.transfer.models import SiteID
from byceps.services.user import creation_service as user_creation_service
from byceps.services.user.creation_service import UserCreationFailed
from byceps.services.user.dbmodels.detail import UserDetail as DbUserDetail
from byceps.services.user.dbmodels.user import User as DbUser
from byceps.typing import BrandID, PartyID, UserID


_CONFIG_PATH = Path('../config')
CONFIG_FILENAME_TEST_SITE = _CONFIG_PATH / 'test_site.py'
CONFIG_FILENAME_TEST_ADMIN = _CONFIG_PATH / 'test_admin.py'


def create_admin_app(
    config_overrides: Optional[dict[str, Any]] = None
) -> Flask:
    return create_app(
        config_filename=CONFIG_FILENAME_TEST_ADMIN,
        config_overrides=config_overrides,
    )


def create_site_app(config_overrides: Optional[dict[str, Any]] = None) -> Flask:
    return create_app(
        config_filename=CONFIG_FILENAME_TEST_SITE,
        config_overrides=config_overrides,
    )


def generate_token(n: int = 4) -> str:
    return token_hex(n)


@contextmanager
def app_context(
    *, config_filename: Optional[Union[Path, str]] = CONFIG_FILENAME_TEST_SITE
):
    app = create_app(config_filename=config_filename)

    with app.app_context():
        yield app


@contextmanager
def current_party_set(app: Flask, party: Party):
    def handler(sender, **kwargs):
        g.party_id = party.id
        g.brand_id = party.brand_id

    with appcontext_pushed.connected_to(handler, app):
        yield


@contextmanager
def current_user_set(app: Flask, current_user: CurrentUser):
    def handler(sender, **kwargs):
        g.user = current_user

    with appcontext_pushed.connected_to(handler, app):
        yield


DEFAULT_DATE_OF_BIRTH = date(1993, 2, 15)


def create_user(
    screen_name: Optional[str] = '__random__',
    *,
    email_address: Optional[str] = None,
    email_address_verified: bool = False,
    initialized: bool = True,
    suspended: bool = False,
    deleted: bool = False,
    legacy_id: Optional[str] = None,
    first_names: Optional[str] = 'John Joseph',
    last_name: Optional[str] = 'Doe',
    date_of_birth=DEFAULT_DATE_OF_BIRTH,
    country: Optional[str] = 'State of Mind',
    zip_code: Optional[str] = '31337',
    city: Optional[str] = 'Atrocity',
    street: Optional[str] = 'Elite Street 1337',
    phone_number: Optional[str] = '555-CALL-ME-MAYBE',
    password: str = 'hunter2',
) -> DbUser:
    if screen_name == '__random__':
        screen_name = generate_token(8)

    user_id = UserID(generate_uuid())

    created_at = datetime.utcnow()

    if not email_address:
        email_address = f'user{user_id}@users.test'

    user = user_creation_service.build_db_user(
        created_at, screen_name, email_address
    )

    user.id = user_id
    user.email_address_verified = email_address_verified
    user.initialized = initialized
    user.suspended = suspended
    user.deleted = deleted
    user.legacy_id = legacy_id

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

    password_service.create_password_hash(user.id, password)

    return user


def create_permissions(permission_ids: Iterable[PermissionID]) -> None:
    for permission_id in permission_ids:
        authz_service.create_permission(
            permission_id, permission_id, ignore_if_exists=True
        )


def create_role_with_permissions_assigned(
    role_id: RoleID, permission_ids: Iterable[PermissionID]
) -> None:
    role = authz_service.create_role(role_id, role_id, ignore_if_exists=True)

    for permission_id in permission_ids:
        authz_service.assign_permission_to_role(permission_id, role_id)


def create_party(
    brand_id: BrandID,
    party_id: PartyID = PartyID('acmecon-2014'),
    title: str = 'ACMECon 2014',
) -> Party:
    starts_at = datetime(2014, 10, 24, 16, 0)
    ends_at = datetime(2014, 10, 26, 13, 0)

    return party_service.create_party(
        party_id, brand_id, title, starts_at, ends_at
    )


def create_site(
    site_id: SiteID,
    brand_id: BrandID,
    *,
    title: Optional[str] = None,
    server_name: Optional[str] = None,
    enabled: bool = True,
    user_account_creation_enabled: bool = True,
    login_enabled: bool = True,
    party_id: Optional[PartyID] = None,
    board_id: Optional[BoardID] = None,
    storefront_id: Optional[StorefrontID] = None,
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
        board_id=board_id,
        storefront_id=storefront_id,
    )


@contextmanager
def http_client(app: Flask, *, user_id: Optional[UserID] = None):
    """Provide an HTTP client.

    If a user ID is given, the client authenticates with the user's
    credentials.
    """
    client = app.test_client()

    if user_id is not None:
        _add_user_credentials_to_session(client, user_id)

    yield client


def _add_user_credentials_to_session(client, user_id: UserID) -> None:
    session_token = session_service.find_session_token_for_user(user_id)
    if session_token is None:
        raise Exception(f'Could not find session token for user ID "{user_id}"')

    with client.session_transaction() as session:
        session['user_id'] = str(user_id)
        session['user_auth_token'] = str(session_token.token)


def login_user(user_id: UserID) -> None:
    """Authenticate the user to create a session."""
    session_service.get_session_token(user_id)
