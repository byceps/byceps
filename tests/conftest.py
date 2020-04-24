"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Optional

import pytest

from byceps.services.brand import service as brand_service
from byceps.services.email import service as email_service
from byceps.services.party import service as party_service
from byceps.services.site import service as site_service
from byceps.services.user import (
    command_service as user_command_service,
    service as user_service,
)

from tests.base import create_admin_app, create_party_app
from tests.database import set_up_database, tear_down_database
from tests.helpers import (
    create_brand,
    create_party,
    create_site,
    create_user,
    create_user_with_detail,
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
def admin_client(admin_app):
    """Provide a test HTTP client against the admin web application."""
    return admin_app.test_client()


@pytest.fixture(scope='session')
def make_party_app(admin_app, data_path):
    """Provide a party web application."""

    def _wrapper(**config_overrides):
        if CONFIG_PATH_DATA_KEY not in config_overrides:
            config_overrides[CONFIG_PATH_DATA_KEY] = data_path
        return create_party_app(config_overrides)

    return _wrapper


@pytest.fixture(scope='session')
def party_app(make_party_app):
    """Provide a party web application."""
    app = make_party_app()
    with app.app_context():
        yield app


@pytest.fixture(scope='session')
def data_path():
    with TemporaryDirectory() as d:
        yield Path(d)


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


@pytest.fixture(scope='module')
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
def make_email_config(admin_app):
    def _wrapper(
        config_id: str,
        sender_address: str,
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


@pytest.fixture(scope='session')
def email_config(make_email_config):
    return make_email_config(
        DEFAULT_EMAIL_CONFIG_ID, sender_address='noreply@acmecon.test'
    )


@pytest.fixture(scope='session')
def site(email_config, party):
    site = create_site(
        'acmecon-2014-website',
        title='ACMECon 2014 website',
        server_name='www.acmecon.test',
        party_id=party.id,
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
