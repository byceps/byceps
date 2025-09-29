"""
:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from flask_babel import Babel
from moneyed import EUR, Money
import pytest

from byceps.byceps_app import BycepsApp
from byceps.config.models import (
    AppMode,
    AppsConfig,
    BycepsConfig,
    DatabaseConfig,
    DevelopmentConfig,
    JobsConfig,
    MetricsConfig,
    PaymentGatewaysConfig,
    RedisConfig,
    SmtpConfig,
)
from byceps.services.brand.models import Brand, BrandID
from byceps.services.party.models import Party, PartyID
from byceps.services.shop.order.models.order import Orderer
from byceps.services.shop.product.models import (
    Product,
    ProductID,
    ProductNumber,
    ProductType,
)
from byceps.services.shop.shop.models import ShopID
from byceps.services.user.models.user import User, UserID

from tests.helpers import generate_token, generate_uuid


@pytest.fixture(scope='session')
def make_byceps_config():
    def _wrapper() -> BycepsConfig:
        apps_config = AppsConfig(admin=None, api=None, sites=[])

        return BycepsConfig(
            data_path=Path('./data'),
            locale='de',
            propagate_exceptions=None,
            testing=True,
            timezone='Europe/Berlin',
            secret_key='secret-key-for-testing-ONLY',
            apps=apps_config,
            database=DatabaseConfig(
                host='127.0.0.1',
                port=5432,
                username='dbusername',
                password='dbpassword',
                database='database',
            ),
            development=DevelopmentConfig(
                style_guide_enabled=False,
                toolbar_enabled=False,
            ),
            discord=None,
            invoiceninja=None,
            jobs=JobsConfig(
                asynchronous=False,
            ),
            metrics=MetricsConfig(
                enabled=False,
            ),
            payment_gateways=PaymentGatewaysConfig(
                paypal=None,
                stripe=None,
            ),
            redis=RedisConfig(
                url='redis://127.0.0.1:6379/0',
            ),
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

    return _wrapper


@pytest.fixture(scope='session')
def make_app(make_byceps_config):
    def _wrapper(
        app_mode: AppMode,
        *,
        site_id: str | None = None,
        additional_config: dict[str, Any] | None = None,
    ) -> BycepsApp:
        byceps_config = make_byceps_config()

        app = BycepsApp(app_mode, byceps_config, site_id)

        if additional_config is not None:
            app.config.from_mapping(additional_config)

        Babel(app)

        return app

    return _wrapper


@pytest.fixture(scope='session')
def app(make_app):
    return make_app(AppMode.site)


@pytest.fixture(scope='session')
def make_user():
    def _wrapper(
        *,
        user_id: UserID | None = None,
        screen_name: str | None = '__random__',
        initialized: bool = True,
        suspended: bool = False,
        deleted: bool = False,
    ) -> User:
        if user_id is None:
            user_id = UserID(generate_uuid())

        if screen_name == '__random__':
            screen_name = generate_token()

        return User(
            id=user_id,
            screen_name=screen_name,
            initialized=initialized,
            suspended=suspended,
            deleted=deleted,
            locale=None,
            avatar_url='/static/user_avatar_fallback.svg',
        )

    return _wrapper


@pytest.fixture(scope='session')
def admin_user(make_user) -> User:
    return make_user()


@pytest.fixture(scope='session')
def user(make_user):
    return make_user()


@pytest.fixture(scope='session')
def deleted_user(make_user):
    return make_user(deleted=True)


@pytest.fixture(scope='session')
def suspended_user(make_user):
    return make_user(suspended=True)


@pytest.fixture(scope='session')
def brand() -> Brand:
    return Brand(
        id=BrandID(generate_token()),
        title=generate_token(),
        image_filename=None,
        image_url_path=None,
        archived=False,
    )


@pytest.fixture(scope='session')
def make_party(brand: Brand):
    def _wrapper(
        *, starts_at: datetime | None = None, ends_at: datetime | None = None
    ) -> Party:
        if starts_at is None:
            starts_at = datetime.utcnow()

        if ends_at is None:
            ends_at = datetime.utcnow()

        return Party(
            id=PartyID(generate_token()),
            brand_id=brand.id,
            title=generate_token(),
            starts_at=starts_at,
            ends_at=ends_at,
            max_ticket_quantity=0,
            ticket_management_enabled=False,
            seat_management_enabled=False,
            hidden=False,
            canceled=False,
            archived=False,
        )

    return _wrapper


@pytest.fixture(scope='session')
def party(brand: Brand, make_party) -> Party:
    return make_party()


@pytest.fixture(scope='session')
def make_product():
    def _wrapper(
        *,
        price: Money | None = None,
        available_from: datetime | None = None,
        available_until: datetime | None = None,
        total_quantity: int = 100,
        quantity: int = 1,
        max_quantity_per_order: int = 10,
    ) -> Product:
        if price is None:
            price = Money('1.99', EUR)

        return Product(
            id=ProductID(generate_uuid()),
            shop_id=ShopID(generate_token()),
            item_number=ProductNumber(generate_token()),
            type_=ProductType.other,
            type_params={},
            name=generate_token(),
            price=price,
            tax_rate=Decimal('0.19'),
            available_from=available_from,
            available_until=available_until,
            total_quantity=total_quantity,
            quantity=quantity,
            max_quantity_per_order=max_quantity_per_order,
            not_directly_orderable=False,
            separate_order_required=False,
            processing_required=False,
            archived=False,
        )

    return _wrapper


@pytest.fixture(scope='session')
def orderer(make_user) -> Orderer:
    return Orderer(
        user=make_user(),
        company=None,
        first_name='John',
        last_name='Wick',
        country='Germany',
        postal_code='22999',
        city='Büttenwarder',
        street='Deichweg 1',
    )
