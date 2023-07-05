"""
tests.helpers
~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from collections.abc import Iterable
from contextlib import contextmanager
from datetime import date, datetime
from pathlib import Path
from secrets import token_hex
from typing import Any
from uuid import UUID

from flask import appcontext_pushed, Flask, g
from uuid6 import uuid7

from byceps.application import (
    create_admin_app as _create_admin_app,
    create_app,
    create_site_app as _create_site_app,
)
from byceps.database import db
from byceps.services.authentication.session import authn_session_service
from byceps.services.authentication.session.models import CurrentUser
from byceps.services.authorization import authz_service
from byceps.services.authorization.models import PermissionID, RoleID
from byceps.services.board.models import BoardID
from byceps.services.party import party_service
from byceps.services.party.models import Party
from byceps.services.shop.storefront.models import StorefrontID
from byceps.services.site import site_service
from byceps.services.site.models import SiteID
from byceps.services.user import user_creation_service, user_service
from byceps.services.user.models.user import User
from byceps.typing import BrandID, PartyID, UserID


CONFIG_FILENAME_TESTING = Path('..') / 'config' / 'testing.toml'


def create_admin_app(config_overrides: dict[str, Any] | None = None) -> Flask:
    if config_overrides is None:
        config_overrides = {}

    config_overrides['SERVER_NAME'] = 'admin.acmecon.test'

    return _create_admin_app(
        config_filename=CONFIG_FILENAME_TESTING,
        config_overrides=config_overrides,
    )


def create_site_app(
    site_id: SiteID, config_overrides: dict[str, Any] | None = None
) -> Flask:
    if config_overrides is None:
        config_overrides = {}

    config_overrides['SERVER_NAME'] = 'www.acmecon.test'
    config_overrides['SITE_ID'] = site_id

    return _create_site_app(
        config_filename=CONFIG_FILENAME_TESTING,
        config_overrides=config_overrides,
    )


def generate_token(n: int = 4) -> str:
    return token_hex(n)


def generate_uuid() -> UUID:
    return uuid7()


@contextmanager
def app_context(
    *, config_filename: Path | str | None = CONFIG_FILENAME_TESTING
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
    screen_name: str | None = '__random__',
    *,
    email_address: str | None = None,
    email_address_verified: bool = False,
    initialized: bool = True,
    suspended: bool = False,
    deleted: bool = False,
    locale: str | None = None,
    legacy_id: str | None = None,
    first_name: str | None = 'John Joseph',
    last_name: str | None = 'Doe',
    date_of_birth=DEFAULT_DATE_OF_BIRTH,
    country: str | None = 'State of Mind',
    zip_code: str | None = '31337',
    city: str | None = 'Atrocity',
    street: str | None = 'Elite Street 1337',
    phone_number: str | None = '555-CALL-ME-MAYBE',
    password: str = 'hunter2',
) -> User:
    if screen_name == '__random__':
        screen_name = generate_token(8)

    if not email_address:
        email_address = f'user{generate_token(6)}@users.test'

    user, event = user_creation_service.create_user(
        screen_name,
        email_address,
        password,
        locale=locale,
        legacy_id=legacy_id,
        first_name=first_name,
        last_name=last_name,
        date_of_birth=date_of_birth,
        country=country,
        zip_code=zip_code,
        city=city,
        street=street,
        phone_number=phone_number,
    ).unwrap()

    if email_address_verified or initialized or suspended or deleted:
        db_user = user_service.get_db_user(user.id)
        db_user.email_address_verified = email_address_verified
        db_user.initialized = initialized
        db_user.suspended = suspended
        db_user.deleted = deleted
        db.session.commit()

    return user


def create_role_with_permissions_assigned(
    role_id: RoleID, permission_ids: Iterable[PermissionID]
) -> None:
    role = authz_service.create_role(role_id, role_id).unwrap()

    for permission_id in permission_ids:
        authz_service.assign_permission_to_role(permission_id, role.id)


def create_party(
    brand_id: BrandID,
    party_id: PartyID | None = None,
    title: str | None = None,
    *,
    max_ticket_quantity: int | None = None,
) -> Party:
    if party_id is None:
        party_id = PartyID(generate_token())

    if title is None:
        title = generate_token()

    starts_at = datetime(2014, 10, 24, 16, 0)
    ends_at = datetime(2014, 10, 26, 13, 0)

    return party_service.create_party(
        party_id,
        brand_id,
        title,
        starts_at,
        ends_at,
        max_ticket_quantity=max_ticket_quantity,
    )


def create_site(
    site_id: SiteID,
    brand_id: BrandID,
    *,
    title: str | None = None,
    server_name: str | None = None,
    enabled: bool = True,
    user_account_creation_enabled: bool = True,
    login_enabled: bool = True,
    party_id: PartyID | None = None,
    board_id: BoardID | None = None,
    storefront_id: StorefrontID | None = None,
    is_intranet: bool = False,
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
        is_intranet=is_intranet,
    )


@contextmanager
def http_client(app: Flask, *, user_id: UserID | None = None):
    """Provide an HTTP client.

    If a user ID is given, the client authenticates with the user's
    credentials.
    """
    client = app.test_client()

    if user_id is not None:
        _add_user_credentials_to_session(client, user_id)

    yield client


def _add_user_credentials_to_session(client, user_id: UserID) -> None:
    session_token = authn_session_service.find_session_token_for_user(user_id)
    if session_token is None:
        raise Exception(f'Could not find session token for user ID "{user_id}"')

    with client.session_transaction() as session:
        session['user_id'] = str(user_id)
        session['user_auth_token'] = str(session_token.token)


def log_in_user(user_id: UserID) -> None:
    """Authenticate the user to create a session."""
    authn_session_service.get_session_token(user_id)
