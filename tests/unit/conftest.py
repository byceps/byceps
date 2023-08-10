"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from datetime import datetime

import pytest

from byceps.services.brand.models import Brand
from byceps.services.party.models import Party
from byceps.services.shop.order.models.order import Orderer
from byceps.services.user.models.user import User
from byceps.typing import BrandID, PartyID, UserID

from tests.helpers import generate_token, generate_uuid


@pytest.fixture(scope='session')
def make_user():
    def _wrapper(
        *,
        screen_name: str | None = '__random__',
        suspended: bool = False,
        deleted: bool = False,
    ) -> User:
        if screen_name == '__random__':
            screen_name = generate_token()

        return User(
            id=UserID(generate_uuid()),
            screen_name=screen_name,
            suspended=suspended,
            deleted=deleted,
            locale=None,
            avatar_url=None,
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
            canceled=False,
            archived=False,
        )

    return _wrapper


@pytest.fixture(scope='session')
def party(brand: Brand, make_party) -> Party:
    return make_party()


@pytest.fixture(scope='session')
def orderer(make_user) -> Orderer:
    return Orderer(
        user=make_user(),
        company=None,
        first_name='John',
        last_name='Wick',
        country='Germany',
        zip_code='22999',
        city='Büttenwarder',
        street='Deichweg 1',
    )
