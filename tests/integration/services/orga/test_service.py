"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.services.orga import service as orga_service


def test_flag_changes(brand, admin_user, user):
    assert not orga_service.is_user_orga(user.id)

    flag = orga_service.add_orga_flag(brand.id, user.id, admin_user.id)

    assert orga_service.is_user_orga(user.id)

    orga_service.remove_orga_flag(flag, admin_user.id)

    assert not orga_service.is_user_orga(user.id)
