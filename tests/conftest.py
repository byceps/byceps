"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from pathlib import Path
from secrets import token_hex
from tempfile import TemporaryDirectory
from typing import Optional, Set

import pytest

from byceps.services.authorization import service as authz_service
from byceps.services.board import board_service
from byceps.services.brand import service as brand_service
from byceps.services.email import service as email_service
from byceps.services.party import service as party_service
from byceps.services.site import service as site_service
from byceps.services.user import (
    command_service as user_command_service,
    service as user_service,
)
from byceps.typing import BrandID

from tests.base import create_admin_app, create_site_app
from tests.database import set_up_database, tear_down_database
from tests.helpers import (
    create_brand,
    create_party,
    create_permissions,
    create_role_with_permissions_assigned,
    create_site,
    create_user,
    create_user_with_detail,
    http_client,
    DEFAULT_EMAIL_CONFIG_ID,
)


CONFIG_PATH_DATA_KEY = 'PATH_DATA'


@pytest.fixture(scope='session')
def make_admin_app(data_path):
    """Provide the admin web application."""

    def _wrapper(**config_overrides):
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

    def _wrapper(**config_overrides):
        if CONFIG_PATH_DATA_KEY not in config_overrides:
            config_overrides[CONFIG_PATH_DATA_KEY] = data_path
        return create_site_app(config_overrides)

    return _wrapper


@pytest.fixture(scope='session')
def site_app(make_site_app):
    """Provide a site web application."""
    app = make_site_app()
    with app.app_context():
        yield app


@pytest.fixture(scope='session')
def data_path():
    with TemporaryDirectory() as d:
        yield Path(d)


@pytest.fixture(scope='package')
def make_client():
    """Provide a test HTTP client against the application."""

    def _wrapper(app, *, user_id=None):
        with http_client(app, user_id=user_id) as client:
            return client

    return _wrapper


@pytest.fixture(scope='session')
def make_user(admin_app):
    user_ids = set()

    def _wrapper(*args, **kwargs):
        user = create_user(*args, **kwargs)
        user_ids.add(user.id)
        user_dto = user_service._db_entity_to_user(user)
        return user_dto

    yield _wrapper

    for user_id in user_ids:
        user_command_service.delete_account(user_id, user_id, 'clean up')


@pytest.fixture(scope='session')
def make_user_with_detail(admin_app):
    user_ids = set()

    def _wrapper(*args, **kwargs):
        user = create_user_with_detail(*args, **kwargs)
        user_ids.add(user.id)
        user_dto = user_service._db_entity_to_user_with_detail(user)
        return user_dto

    yield _wrapper

    for user_id in user_ids:
        user_command_service.delete_account(user_id, user_id, 'clean up')


@pytest.fixture(scope='session')
def make_admin(make_user):
    user_ids = set()
    created_permission_ids = set()
    created_role_ids = set()

    def _wrapper(screen_name: str, permission_ids: Set[str]):
        admin = make_user(screen_name)
        user_ids.add(admin.id)

        # Create permissions and role.
        role_id = f'admin_{token_hex(3)}'
        create_permissions(permission_ids)
        created_permission_ids.update(permission_ids)
        create_role_with_permissions_assigned(role_id, permission_ids)
        authz_service.assign_role_to_user(role_id, admin.id)
        created_role_ids.add(role_id)

        return admin

    yield _wrapper

    # Remove permissions and role again.

    for user_id in user_ids:
        authz_service.deassign_all_roles_from_user(user_id)

    for role_id in created_role_ids:
        authz_service.delete_role(role_id)

    for permission_id in created_permission_ids:
        authz_service.delete_permission(permission_id)


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


@pytest.fixture(scope='session')
def make_email_config(admin_app, brand):
    configs = []

    def _wrapper(
        config_id: str,
        brand_id: BrandID,
        sender_address: str,
        *,
        sender_name: Optional[str] = None,
        contact_address: Optional[str] = None,
    ):
        email_service.set_config(
            config_id,
            brand_id,
            sender_address,
            sender_name=sender_name,
            contact_address=contact_address,
        )

        config = email_service.get_config(config_id)
        configs.append(config)

        return config

    yield _wrapper

    for config in configs:
        email_service.delete_config(config.id)


# Dependency on `brand` avoids error on clean up.
@pytest.fixture(scope='session')
def email_config(make_email_config, brand):
    return make_email_config(
        DEFAULT_EMAIL_CONFIG_ID, brand.id, sender_address='noreply@acmecon.test'
    )


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
def brand(admin_app):
    brand = create_brand()
    yield brand
    brand_service.delete_brand(brand.id)


@pytest.fixture(scope='session')
def party(brand):
    party = create_party(brand.id)
    yield party
    party_service.delete_party(party.id)


@pytest.fixture(scope='session')
def board(brand):
    board_id = brand.id
    board = board_service.create_board(brand.id, board_id)
    yield board
    board_service.delete_board(board.id)
