"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Optional

import pytest

from byceps.database import db as _db
from byceps.services.brand import service as brand_service
from byceps.services.email import service as email_service
from byceps.services.party import service as party_service
from byceps.services.site import service as site_service
from byceps.services.user import command_service as user_command_service

from tests.base import create_admin_app, create_party_app
from tests.database import set_up_database, tear_down_database
from tests.helpers import (
    create_brand,
    create_party,
    create_site,
    create_user,
    DEFAULT_EMAIL_CONFIG_ID,
)


CONFIG_PATH_DATA_KEY = 'PATH_DATA'


@pytest.fixture(scope='session')
def db():
    return _db


@contextmanager
def database_recreated(db):
    set_up_database(db)

    yield

    tear_down_database(db)


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
    yield make_admin_app()


@pytest.fixture(scope='module')
def admin_app_with_db(admin_app, db):
    with admin_app.app_context():
        with database_recreated(db):
            yield admin_app


@pytest.fixture
def admin_client(admin_app):
    """Provide a test HTTP client against the admin web application."""
    return admin_app.test_client()


@pytest.fixture(scope='module')
def party_app(admin_app_with_db):
    """Provide a party web application."""
    config_overrides = {CONFIG_PATH_DATA_KEY: data_path}
    app = create_party_app(config_overrides)
    with app.app_context():
        yield app


@pytest.fixture(scope='session')
def data_path():
    with TemporaryDirectory() as d:
        yield Path(d)


@pytest.fixture(scope='module')
def make_user(admin_app_with_db):
    def _wrapper(*args, **kwargs):
        user = create_user(*args, **kwargs)
        yield user
        user_command_service.delete_account(user.id, user.id, 'clean up')

    yield _wrapper


@pytest.fixture
def admin_user(make_user):
    yield from make_user('Admin')


@pytest.fixture
def user(make_user):
    yield from make_user('User')


@pytest.fixture
def uninitialized_user(make_user):
    yield from make_user('UninitializedUser', initialized=False)


@pytest.fixture
def suspended_user(make_user):
    yield from make_user('SuspendedUser', suspended=True)


@pytest.fixture
def deleted_user(make_user):
    yield from make_user('DeletedUser', deleted=True)


@pytest.fixture(scope='module')
def make_email_config(admin_app_with_db):
    def _wrapper(
        config_id: str = DEFAULT_EMAIL_CONFIG_ID,
        sender_address: str = 'info@shop.example',
        *,
        sender_name: Optional[str] = None,
        contact_address: Optional[str] = None,
    ):
        email_service.set_config(
            config_id,
            sender_address,
            sender_name=sender_name,
            contact_address=contact_address,
        )

        return email_service.get_config(config_id)

    return _wrapper


@pytest.fixture
def email_config(make_email_config):
    return make_email_config()


@pytest.fixture
def site(email_config):
    site = create_site()
    yield site
    site_service.delete_site(site.id)


@pytest.fixture(scope='module')
def brand(admin_app_with_db):
    brand = create_brand()
    yield brand
    brand_service.delete_brand(brand.id)


@pytest.fixture(scope='module')
def party(brand):
    party = create_party(brand.id)
    yield party
    party_service.delete_party(party.id)
