"""
:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Iterator
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from wsgiref.types import WSGIApplication

from flask import Flask
from moneyed import EUR
import pytest

from byceps.app_dispatcher import create_dispatcher_app
from byceps.application import (
    create_admin_app as _create_admin_app,
    create_site_app as _create_site_app,
)
from byceps.byceps_app import BycepsApp
from byceps.config.converter import assemble_database_uri
from byceps.config.models import (
    AdminWebAppConfig,
    ApiWebAppConfig,
    BycepsConfig,
    DatabaseConfig,
    DevelopmentConfig,
    JobsConfig,
    MetricsConfig,
    PaymentGatewaysConfig,
    RedisConfig,
    SiteWebAppConfig,
    SmtpConfig,
    WebAppsConfig,
)
from byceps.database import db
from byceps.services.authz import authz_service
from byceps.services.authz.models import PermissionID, Role, RoleID
from byceps.services.board import board_service
from byceps.services.board.models import Board, BoardID
from byceps.services.brand import brand_service
from byceps.services.brand.models import Brand, BrandID
from byceps.services.email import email_config_service
from byceps.services.email.models import EmailConfig
from byceps.services.news import news_channel_service
from byceps.services.news.models import NewsChannel, NewsChannelID
from byceps.services.party.models import Party, PartyID
from byceps.services.shop.order import order_sequence_service
from byceps.services.shop.order.models.number import (
    OrderNumberSequence,
    OrderNumberSequenceID,
)
from byceps.services.shop.order.models.order import Orderer
from byceps.services.shop.payment import payment_gateway_service
from byceps.services.shop.payment.models import PaymentGateway
from byceps.services.shop.product.models import Product
from byceps.services.shop.shop import shop_service
from byceps.services.shop.shop.models import Shop, ShopID
from byceps.services.shop.storefront import storefront_service
from byceps.services.shop.storefront.models import (
    Storefront,
    StorefrontID,
)
from byceps.services.site.models import Site, SiteID
from byceps.services.ticketing import ticket_category_service
from byceps.services.ticketing.models.ticket import TicketCategory
from byceps.services.user.models.user import User, UserID

from tests.helpers import (
    create_party,
    create_role_with_permissions_assigned,
    create_site,
    create_user,
    generate_token,
    http_client,
)
from tests.helpers.shop import create_product, create_orderer

from .database import populate_database, set_up_database, tear_down_database


@pytest.fixture(scope='session')
def database_config():
    host = os.environ.get('POSTGRES_HOST', '127.0.0.1')
    port = int(os.environ.get('POSTGRES_PORT', '5432'))
    username = os.environ.get('POSTGRES_USER', 'byceps_test')
    password = os.environ.get('POSTGRES_PASSWORD', 'test')
    database = os.environ.get('POSTGRES_DB', 'byceps_test')

    return DatabaseConfig(
        host=host,
        port=port,
        username=username,
        password=password,
        database=database,
    )


@pytest.fixture(scope='session')
def redis_config():
    host = os.environ.get('REDIS_HOST', '127.0.0.1')
    port = int(os.environ.get('REDIS_PORT', '6379'))
    database = 0

    return RedisConfig(
        url=f'redis://{host}:{port}/{database}',
    )


def build_byceps_config(
    data_path: Path,
    database_config: DatabaseConfig,
    redis_config: RedisConfig,
    *,
    metrics_enabled: bool = False,
    style_guide_enabled: bool = False,
) -> BycepsConfig:
    return BycepsConfig(
        data_path=data_path,
        locale='de',
        propagate_exceptions=None,
        testing=True,
        timezone='Europe/Berlin',
        secret_key='secret-key-for-testing-ONLY',
        database=database_config,
        development=DevelopmentConfig(
            style_guide_enabled=style_guide_enabled,
            toolbar_enabled=False,
        ),
        discord=None,
        invoiceninja=None,
        jobs=JobsConfig(
            asynchronous=False,
        ),
        metrics=MetricsConfig(
            enabled=metrics_enabled,
        ),
        payment_gateways=PaymentGatewaysConfig(
            paypal=None,
            stripe=None,
        ),
        redis=redis_config,
        smtp=SmtpConfig(
            host='127.0.0.1',
            port=25,
            starttls=False,
            use_ssl=False,
            username=None,
            password=None,
            suppress_send=True,
        ),
    )


@pytest.fixture(scope='session')
def database(database_config: DatabaseConfig):
    app = Flask('byceps')

    app.config['SQLALCHEMY_DATABASE_URI'] = assemble_database_uri(
        database_config
    )

    db.init_app(app)

    with app.app_context():
        # tear_down_database()
        set_up_database()
        populate_database()


@pytest.fixture(scope='session')
def apps(database, make_byceps_config) -> WSGIApplication:
    byceps_config = make_byceps_config()

    web_apps_config = WebAppsConfig(
        admin=None,
        api=ApiWebAppConfig(server_name='api.acmecon.test'),
        sites=[],
    )

    return create_dispatcher_app(byceps_config, web_apps_config)


@pytest.fixture(scope='session')
def make_admin_app(make_byceps_config):
    """Provide the admin web application."""

    def _wrapper(
        server_name: str,
        *,
        metrics_enabled: bool = False,
        style_guide_enabled: bool = False,
    ) -> BycepsApp:
        byceps_config = make_byceps_config(
            metrics_enabled=metrics_enabled,
            style_guide_enabled=style_guide_enabled,
        )

        app_config = AdminWebAppConfig(
            server_name=server_name,
        )

        return _create_admin_app(byceps_config, app_config)

    return _wrapper


@pytest.fixture(scope='session')
def admin_app(database, make_admin_app) -> Iterator[BycepsApp]:
    """Provide the admin web application."""
    server_name = 'admin.acmecon.test'
    app = make_admin_app(server_name)
    with app.app_context():
        yield app


@pytest.fixture(scope='session')
def api_app(apps, site: Site) -> BycepsApp:
    """Provide a API web application."""
    server_name = 'api.acmecon.test'
    app = apps.wsgi_app.get_application(server_name)
    with app.app_context():
        return app


@pytest.fixture(scope='session')
def make_site_app(admin_app, make_byceps_config):
    """Provide a site web application."""

    def _wrapper(
        server_name: str, site_id: SiteID, *, style_guide_enabled: bool = False
    ) -> BycepsApp:
        byceps_config = make_byceps_config(
            style_guide_enabled=style_guide_enabled
        )

        app_config = SiteWebAppConfig(
            server_name=server_name,
            site_id=site_id,
        )

        return _create_site_app(byceps_config, app_config)

    return _wrapper


@pytest.fixture(scope='session')
def site_app(database, make_site_app, site: Site) -> BycepsApp:
    """Provide a site web application."""
    server_name = 'www.acmecon.test'
    app = make_site_app(server_name, site.id)
    with app.app_context():
        return app


@pytest.fixture(scope='session')
def make_byceps_config(
    data_path: Path, database_config: DatabaseConfig, redis_config: RedisConfig
):
    def _wrapper(
        *,
        metrics_enabled: bool = False,
        style_guide_enabled: bool = False,
    ) -> BycepsConfig:
        return build_byceps_config(
            data_path,
            database_config,
            redis_config,
            metrics_enabled=metrics_enabled,
            style_guide_enabled=style_guide_enabled,
        )

    return _wrapper


@pytest.fixture(scope='session')
def data_path() -> Path:
    with TemporaryDirectory() as d:
        return Path(d)


@pytest.fixture(scope='package')
def make_client():
    """Provide a test HTTP client against the application."""

    def _wrapper(app: BycepsApp, *, user_id: UserID | None = None):
        with http_client(app, user_id=user_id) as client:
            return client

    return _wrapper


@pytest.fixture(scope='session')
def make_role(admin_app: BycepsApp):
    def _wrapper() -> Role:
        role_id = RoleID(generate_token())
        return authz_service.create_role(role_id, role_id).unwrap()

    return _wrapper


@pytest.fixture(scope='session')
def make_user(admin_app: BycepsApp):
    def _wrapper(*args, **kwargs) -> User:
        return create_user(*args, **kwargs)

    return _wrapper


@pytest.fixture(scope='session')
def make_admin(make_user):
    def _wrapper(permission_id_strs: set[str], *args, **kwargs) -> User:
        admin = make_user(*args, **kwargs)

        # Create role.
        role_id = RoleID(f'admin_{generate_token()}')
        permission_ids = [PermissionID(p_id) for p_id in permission_id_strs]
        create_role_with_permissions_assigned(role_id, permission_ids)

        # Assign role to user.
        authz_service.assign_role_to_user(role_id, admin)

        return admin

    return _wrapper


@pytest.fixture(scope='session')
def admin_user(make_admin) -> User:
    permission_ids = {'admin.access'}
    return make_admin(permission_ids, screen_name='Admin')


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
def make_email_config(admin_app: BycepsApp):
    def _wrapper(
        brand_id: BrandID,
        *,
        sender_address: str | None = None,
        sender_name: str | None = None,
        contact_address: str | None = None,
    ) -> EmailConfig:
        if sender_address is None:
            sender_address = f'{generate_token()}@domain.example'

        email_config_service.set_config(
            brand_id,
            sender_address,
            sender_name=sender_name,
            contact_address=contact_address,
        )

        return email_config_service.get_config(brand_id)

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
def site(email_config: EmailConfig, party: Party, board: Board) -> Site:
    return create_site(
        SiteID('acmecon-2014-website'),
        party.brand_id,
        title='ACMECon 2014 website',
        server_name='www.acmecon.test',
        party_id=party.id,
        board_id=board.id,
    )


@pytest.fixture(scope='session')
def make_brand(admin_app: BycepsApp):
    def _wrapper(
        brand_id: BrandID | None = None, title: str | None = None
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
def make_party(admin_app: BycepsApp):
    def _wrapper(*args, **kwargs) -> Party:
        return create_party(*args, **kwargs)

    return _wrapper


@pytest.fixture(scope='session')
def party(make_party, brand: Brand) -> Party:
    return make_party(brand, title='ACMECon 2014')


@pytest.fixture(scope='session')
def make_ticket_category(admin_app: BycepsApp):
    def _wrapper(party_id: PartyID, title: str) -> TicketCategory:
        return ticket_category_service.create_category(party_id, title)

    return _wrapper


@pytest.fixture(scope='session')
def board(brand: Brand) -> Board:
    board_id = BoardID(generate_token())
    return board_service.create_board(brand, board_id)


@pytest.fixture()
def make_news_channel():
    def _wrapper(
        brand: Brand,
        channel_id: NewsChannelID | None = None,
        *,
        announcement_site_id: SiteID | None = None,
    ) -> NewsChannel:
        if channel_id is None:
            channel_id = NewsChannelID(generate_token())

        return news_channel_service.create_channel(
            brand, channel_id, announcement_site_id=announcement_site_id
        )

    return _wrapper


@pytest.fixture(scope='session')
def make_payment_gateway(admin_app: BycepsApp):
    def _wrapper(
        *,
        payment_gateway_id: str | None = None,
        name: str | None = None,
        enabled: bool = True,
    ) -> PaymentGateway:
        if payment_gateway_id is None:
            payment_gateway_id = generate_token()

        if name is None:
            name = payment_gateway_id

        return payment_gateway_service.create_payment_gateway(
            payment_gateway_id, name, enabled
        )

    return _wrapper


@pytest.fixture(scope='session')
def make_shop(admin_app: BycepsApp):
    def _wrapper(brand: Brand) -> Shop:
        return shop_service.create_shop(brand, EUR)

    return _wrapper


@pytest.fixture(scope='session')
def make_order_number_sequence():
    def _wrapper(
        shop_id: ShopID,
        *,
        prefix: str | None = None,
        value: int = 0,
    ) -> OrderNumberSequence:
        if prefix is None:
            prefix = f'{generate_token()}-O'

        return order_sequence_service.create_order_number_sequence(
            shop_id, prefix, value=value
        ).unwrap()

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


@pytest.fixture(scope='session')
def make_product():
    def _wrapper(shop_id: ShopID, **kwargs) -> Product:
        return create_product(shop_id, **kwargs)

    return _wrapper


@pytest.fixture(scope='session')
def make_orderer():
    def _wrapper(user: User) -> Orderer:
        return create_orderer(user)

    return _wrapper
