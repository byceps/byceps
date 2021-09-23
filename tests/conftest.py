"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from pathlib import Path
from secrets import token_hex
from tempfile import TemporaryDirectory
from typing import Any, Optional

from flask import Flask
import pytest

from byceps.services.authorization import service as authz_service
from byceps.services.board import board_service
from byceps.services.brand import service as brand_service
from byceps.services.brand.transfer.models import Brand
from byceps.services.email import service as email_service
from byceps.services.email.transfer.models import EmailConfig
from byceps.services.party import service as party_service
from byceps.services.party.transfer.models import Party
from byceps.services.site import service as site_service
from byceps.services.ticketing import (
    category_service as ticketing_category_service,
)
from byceps.services.ticketing.transfer.models import TicketCategory
from byceps.services.user import (
    command_service as user_command_service,
    deletion_service as user_deletion_service,
)
from byceps.services.user.transfer.models import User
from byceps.typing import BrandID, PartyID, UserID

from tests.database import set_up_database, tear_down_database
from tests.helpers import (
    create_admin_app,
    create_party,
    create_role_with_permissions_assigned,
    create_site,
    create_site_app,
    create_user,
    generate_token,
    http_client,
)


CONFIG_PATH_DATA_KEY = 'PATH_DATA'


@pytest.fixture(scope='session')
def make_admin_app(data_path):
    """Provide the admin web application."""

    def _wrapper(**config_overrides: dict[str, Any]) -> Flask:
        if CONFIG_PATH_DATA_KEY not in config_overrides:
            config_overrides[CONFIG_PATH_DATA_KEY] = data_path
        return create_admin_app(config_overrides)

    return _wrapper


@pytest.fixture(scope='session')
def admin_app(make_admin_app):
    """Provide the admin web application."""
    app = make_admin_app()
    with app.app_context():
        set_up_database()
        yield app
        tear_down_database()


@pytest.fixture(scope='session')
def make_site_app(admin_app, data_path):
    """Provide a site web application."""

    def _wrapper(**config_overrides: dict[str, Any]) -> Flask:
        if CONFIG_PATH_DATA_KEY not in config_overrides:
            config_overrides[CONFIG_PATH_DATA_KEY] = data_path
        return create_site_app(config_overrides)

    return _wrapper


@pytest.fixture(scope='session')
def site_app(make_site_app):
    """Provide a site web application."""
    app = make_site_app()
    with app.app_context():
        return app


@pytest.fixture(scope='session')
def data_path():
    with TemporaryDirectory() as d:
        return Path(d)


@pytest.fixture(scope='package')
def make_client():
    """Provide a test HTTP client against the application."""

    def _wrapper(app: Flask, *, user_id: Optional[UserID] = None):
        with http_client(app, user_id=user_id) as client:
            return client

    return _wrapper


@pytest.fixture(scope='session')
def make_user(admin_app):
    user_ids = set()

    def _wrapper(*args, **kwargs) -> User:
        user = create_user(*args, **kwargs)
        user_ids.add(user.id)
        return user

    yield _wrapper

    for user_id in user_ids:
        user_deletion_service.delete_account(user_id, user_id, 'clean up')


@pytest.fixture(scope='session')
def make_admin(make_user):
    user_ids = set()
    created_role_ids = set()

    def _wrapper(
        screen_name: str, permission_ids: set[str], *args, **kwargs
    ) -> User:
        admin = make_user(screen_name, *args, **kwargs)
        user_ids.add(admin.id)

        # Create role.
        role_id = f'admin_{token_hex(3)}'
        create_role_with_permissions_assigned(role_id, permission_ids)
        created_role_ids.add(role_id)

        # Assign role to user.
        authz_service.assign_role_to_user(role_id, admin.id)

        return admin

    yield _wrapper

    # Remove permissions and role again.

    for user_id in user_ids:
        authz_service.deassign_all_roles_from_user(user_id)

    for role_id in created_role_ids:
        authz_service.delete_role(role_id)


@pytest.fixture(scope='session')
def admin_user(make_user):
    return make_user('Admin')


@pytest.fixture(scope='session')
def user(make_user):
    return make_user('User')


@pytest.fixture(scope='session')
def uninitialized_user(make_user):
    return make_user('UninitializedUser', initialized=False)


@pytest.fixture(scope='session')
def suspended_user(make_user):
    return make_user('SuspendedUser', suspended=True)


@pytest.fixture(scope='session')
def deleted_user(make_user):
    return make_user('DeletedUser', deleted=True)


# Dependency on `brand` avoids error on clean up.
@pytest.fixture(scope='session')
def make_email_config(admin_app, brand):
    config_brand_ids = set()

    def _wrapper(
        brand_id: BrandID,
        *,
        sender_address: Optional[str] = None,
        sender_name: Optional[str] = None,
        contact_address: Optional[str] = None,
    ) -> EmailConfig:
        if sender_address is None:
            sender_address = f'{generate_token()}@domain.example'

        email_service.set_config(
            brand_id,
            sender_address,
            sender_name=sender_name,
            contact_address=contact_address,
        )

        config = email_service.get_config(brand_id)
        config_brand_ids.add(config.brand_id)

        return config

    yield _wrapper

    for brand_id in config_brand_ids:
        email_service.delete_config(brand_id)


@pytest.fixture(scope='session')
def email_config(make_email_config, brand) -> EmailConfig:
    return make_email_config(brand.id, sender_address='noreply@acmecon.test')


@pytest.fixture(scope='session')
def site(email_config, party, board):
    site = create_site(
        'acmecon-2014-website',
        party.brand_id,
        title='ACMECon 2014 website',
        server_name='www.acmecon.test',
        party_id=party.id,
        board_id=board.id,
    )
    yield site
    site_service.delete_site(site.id)


@pytest.fixture(scope='session')
def make_brand(admin_app):
    brand_ids = set()

    def _wrapper(
        brand_id: Optional[BrandID] = None, title: Optional[str] = None
    ) -> Brand:
        if brand_id is None:
            brand_id = BrandID(generate_token())

        if title is None:
            title = brand_id

        brand = brand_service.create_brand(brand_id, title)
        brand_ids.add(brand.id)
        return brand

    yield _wrapper

    for brand_id in brand_ids:
        brand_service.delete_brand(brand_id)


@pytest.fixture(scope='session')
def brand(make_brand):
    return make_brand('acmecon', 'ACME Entertainment Convention')


@pytest.fixture(scope='session')
def make_party(admin_app, make_brand):
    party_ids = set()

    def _wrapper(*args, **kwargs) -> Party:
        party = create_party(*args, **kwargs)
        party_ids.add(party.id)
        return party

    yield _wrapper

    for party_id in party_ids:
        party_service.delete_party(party_id)


@pytest.fixture(scope='session')
def party(make_party, brand):
    return make_party(brand.id)


@pytest.fixture(scope='session')
def make_ticket_category(admin_app, party):
    category_ids = set()

    def _wrapper(party_id: PartyID, title: str) -> TicketCategory:
        category = ticketing_category_service.create_category(party_id, title)
        category_ids.add(category.id)
        return category

    yield _wrapper

    for category_id in category_ids:
        ticketing_category_service.delete_category(category_id)


@pytest.fixture(scope='session')
def board(brand):
    board_id = brand.id
    board = board_service.create_board(brand.id, board_id)
    yield board
    board_service.delete_board(board.id)
