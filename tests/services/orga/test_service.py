"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.orga import service as orga_service

from tests.helpers import create_brand


def test_flag_changes(admin_app_with_db, admin_user, user):
    brand = create_brand()

    assert not orga_service.is_user_orga(user.id)

    flag = orga_service.add_orga_flag(brand.id, user.id, admin_user.id)

    assert orga_service.is_user_orga(user.id)

    orga_service.remove_orga_flag(flag, admin_user.id)

    assert not orga_service.is_user_orga(user.id)
