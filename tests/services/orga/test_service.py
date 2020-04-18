"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.brand import service as brand_service
from byceps.services.orga import service as orga_service

from tests.helpers import create_brand


@pytest.fixture
def brand(admin_app_with_db):
    brand = create_brand()
    yield brand
    brand_service.delete_brand(brand.id)


def test_flag_changes(brand, admin_user, user):
    assert not orga_service.is_user_orga(user.id)

    flag = orga_service.add_orga_flag(brand.id, user.id, admin_user.id)

    assert orga_service.is_user_orga(user.id)

    orga_service.remove_orga_flag(flag, admin_user.id)

    assert not orga_service.is_user_orga(user.id)
