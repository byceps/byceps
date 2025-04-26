"""
tests.helpers
~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Iterable
from contextlib import contextmanager
from datetime import date, datetime
from secrets import token_hex
from uuid import UUID

from flask import appcontext_pushed, g
from secret_type import secret
from uuid6 import uuid7

from byceps.byceps_app import BycepsApp
from byceps.database import db
from byceps.services.authn.session import authn_session_service
from byceps.services.authn.session.models import CurrentUser
from byceps.services.authz import authz_service
from byceps.services.authz.models import PermissionID, RoleID
from byceps.services.board.models import BoardID
from byceps.services.brand.models import Brand, BrandID
from byceps.services.party import party_service
from byceps.services.party.models import Party, PartyID
from byceps.services.shop.storefront.models import StorefrontID
from byceps.services.site import site_service
from byceps.services.site.models import SiteID
from byceps.services.user import (
    user_command_service,
    user_creation_service,
    user_service,
)
from byceps.services.user.models.user import User, UserID


def generate_token(n: int = 4) -> str:
    return token_hex(n)


def generate_uuid() -> UUID:
    return uuid7()


@contextmanager
def current_user_set(app: BycepsApp, current_user: CurrentUser):
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
        secret(password),
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

    if initialized:
        user_command_service.initialize_account(user, assign_roles=False)

    if email_address_verified or suspended or deleted:
        db_user = user_service.get_db_user(user.id)
        db_user.email_address_verified = email_address_verified
        db_user.suspended = suspended
        db_user.deleted = deleted
        db.session.commit()

    updated_user = user_service.get_user(user.id)

    return updated_user


def create_role_with_permissions_assigned(
    role_id: RoleID, permission_ids: Iterable[PermissionID]
) -> None:
    role = authz_service.create_role(role_id, role_id).unwrap()

    for permission_id in permission_ids:
        authz_service.assign_permission_to_role(permission_id, role.id)


def create_party(
    brand: Brand,
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
        brand,
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
def http_client(app: BycepsApp, *, user_id: UserID | None = None):
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
