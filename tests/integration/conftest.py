"""
:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from pathlib import Path
from secrets import token_hex
from tempfile import TemporaryDirectory
from typing import Any, Iterator, Optional

from flask import Flask
import pytest

from byceps.services.authorization import service as authz_service
from byceps.services.authorization.transfer.models import PermissionID, RoleID
from byceps.services.board import board_service
from byceps.services.board.transfer.models import Board, BoardID
from byceps.services.brand import service as brand_service
from byceps.services.brand.transfer.models import Brand
from byceps.services.email import service as email_service
from byceps.services.email.transfer.models import EmailConfig
from byceps.services.party.transfer.models import Party
from byceps.services.shop.order import (
    sequence_service as order_sequence_service,
)
from byceps.services.shop.order.transfer.number import (
    OrderNumberSequence,
    OrderNumberSequenceID,
)
from byceps.services.shop.shop import service as shop_service
from byceps.services.shop.shop.transfer.models import Shop, ShopID
from byceps.services.shop.storefront import service as storefront_service
from byceps.services.shop.storefront.transfer.models import (
    Storefront,
    StorefrontID,
)
from byceps.services.site import service as site_service
from byceps.services.site.transfer.models import Site, SiteID
from byceps.services.ticketing import (
    category_service as ticketing_category_service,
)
from byceps.services.ticketing.transfer.models import TicketCategory
from byceps.services.user import command_service as user_command_service
from byceps.services.user.transfer.models import User
from byceps.typing import BrandID, PartyID, UserID

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

from .database import set_up_database, tear_down_database


_CONFIG_PATH_DATA_KEY = 'PATH_DATA'


@pytest.fixture(scope='session')
def make_admin_app(data_path: Path):
    """Provide the admin web application."""

    def _wrapper(**config_overrides: Any) -> Flask:
        if _CONFIG_PATH_DATA_KEY not in config_overrides:
            config_overrides[_CONFIG_PATH_DATA_KEY] = data_path
        return create_admin_app(config_overrides)

    return _wrapper


@pytest.fixture(scope='session')
def admin_app(make_admin_app) -> Iterator[Flask]:
    """Provide the admin web application."""
    app = make_admin_app()
    with app.app_context():
        set_up_database()
        yield app
        tear_down_database()


@pytest.fixture(scope='session')
def make_site_app(admin_app, data_path):
    """Provide a site web application."""

    def _wrapper(site_id: SiteID, **config_overrides: dict[str, Any]) -> Flask:
        if _CONFIG_PATH_DATA_KEY not in config_overrides:
            config_overrides[_CONFIG_PATH_DATA_KEY] = data_path
        return create_site_app(site_id, config_overrides)

    return _wrapper


@pytest.fixture(scope='session')
def site_app(make_site_app, site: Site) -> Flask:
    """Provide a site web application."""
    app = make_site_app(site.id)
    with app.app_context():
        return app


@pytest.fixture(scope='session')
def data_path() -> Path:
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
def make_user(admin_app: Flask):
    def _wrapper(*args, **kwargs) -> User:
        return create_user(*args, **kwargs)

    return _wrapper


@pytest.fixture(scope='session')
def make_admin(make_user):
    def _wrapper(
        screen_name: str, permission_id_strs: set[str], *args, **kwargs
    ) -> User:
        admin = make_user(screen_name, *args, **kwargs)

        # Create role.
        role_id = RoleID(f'admin_{token_hex(3)}')
        permission_ids = [PermissionID(p_id) for p_id in permission_id_strs]
        create_role_with_permissions_assigned(role_id, permission_ids)

        # Assign role to user.
        authz_service.assign_role_to_user(role_id, admin.id)

        return admin

    return _wrapper


@pytest.fixture(scope='session')
def admin_user(make_admin) -> User:
    permission_ids = {'admin.access'}
    return make_admin('Admin', permission_ids)


@pytest.fixture(scope='session')
def user(make_user) -> User:
    return make_user('User')


@pytest.fixture(scope='session')
def uninitialized_user(make_user) -> User:
    return make_user('UninitializedUser', initialized=False)


@pytest.fixture(scope='session')
def suspended_user(make_user) -> User:
    return make_user('SuspendedUser', suspended=True)


@pytest.fixture(scope='session')
def deleted_user(make_user) -> User:
    return make_user('DeletedUser', deleted=True)


@pytest.fixture(scope='session')
def make_email_config(admin_app: Flask):
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

        return email_service.get_config(brand_id)

    return _wrapper


@pytest.fixture(scope='session')
def email_config(make_email_config, brand: Brand) -> EmailConfig:
    return make_email_config(
        brand.id,
        sender_address='noreply@acmecon.test',
        sender_name='ACME Entertainment Convention',
        contact_address='help@acmecon.test',
    )


@pytest.fixture(scope='session')
def site(
    email_config: EmailConfig, party: Party, board: Board
) -> Iterator[Site]:
    site = create_site(
        SiteID('acmecon-2014-website'),
        party.brand_id,
        title='ACMECon 2014 website',
        server_name='www.acmecon.test',
        party_id=party.id,
        board_id=board.id,
    )
    yield site
    site_service.delete_site(site.id)


@pytest.fixture(scope='session')
def make_brand(admin_app: Flask):
    def _wrapper(
        brand_id: Optional[BrandID] = None, title: Optional[str] = None
    ) -> Brand:
        if brand_id is None:
            brand_id = BrandID(generate_token())

        if title is None:
            title = brand_id

        return brand_service.create_brand(brand_id, title)

    return _wrapper


@pytest.fixture(scope='session')
def brand(make_brand) -> Brand:
    return make_brand('acmecon', 'ACME Entertainment Convention')


@pytest.fixture(scope='session')
def make_party(admin_app: Flask):
    def _wrapper(*args, **kwargs) -> Party:
        return create_party(*args, **kwargs)

    return _wrapper


@pytest.fixture(scope='session')
def party(make_party, brand: Brand) -> Party:
    return make_party(brand.id)


@pytest.fixture(scope='session')
def make_ticket_category(admin_app: Flask):
    def _wrapper(party_id: PartyID, title: str) -> TicketCategory:
        return ticketing_category_service.create_category(party_id, title)

    return _wrapper


@pytest.fixture(scope='session')
def board(brand: Brand) -> Board:
    board_id = BoardID(generate_token())
    return board_service.create_board(brand.id, board_id)


@pytest.fixture(scope='session')
def make_shop(admin_app: Flask):
    def _wrapper(
        brand_id: BrandID,
        *,
        shop_id: Optional[ShopID] = None,
        title: Optional[str] = None,
    ) -> Shop:
        if shop_id is None:
            shop_id = ShopID(generate_token())

        if title is None:
            title = shop_id

        return shop_service.create_shop(shop_id, brand_id, title)

    return _wrapper


@pytest.fixture(scope='session')
def make_order_number_sequence():
    def _wrapper(
        shop_id: ShopID,
        *,
        prefix: Optional[str] = None,
        value: Optional[int] = None,
    ) -> OrderNumberSequence:
        if prefix is None:
            prefix = f'{generate_token()}-O'

        return order_sequence_service.create_order_number_sequence(
            shop_id, prefix, value=value
        )

    return _wrapper


@pytest.fixture(scope='session')
def make_storefront():
    def _wrapper(
        shop_id: ShopID, order_number_sequence_id: OrderNumberSequenceID
    ) -> Storefront:
        storefront_id = StorefrontID(generate_token())
        return storefront_service.create_storefront(
            storefront_id, shop_id, order_number_sequence_id, closed=False
        )

    return _wrapper
