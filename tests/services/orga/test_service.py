"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.orga import service as orga_service

from tests.helpers import create_brand, create_user


def test_flag_changes(admin_app_with_db):
    brand = create_brand()

    user = create_user()
    admin = create_user('Admin')

    assert not orga_service.is_user_orga(user.id)

    flag = orga_service.add_orga_flag(brand.id, user.id, admin.id)

    assert orga_service.is_user_orga(user.id)

    orga_service.remove_orga_flag(flag, admin.id)

    assert not orga_service.is_user_orga(user.id)
