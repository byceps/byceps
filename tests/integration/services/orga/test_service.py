"""
:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.services.orga import service as orga_service


def test_flag_changes(brand, admin_user, user):
    assert not is_orga_for_brand(user.id, brand.id)

    orga_service.add_orga_flag(brand.id, user.id, admin_user.id)

    assert is_orga_for_brand(user.id, brand.id)

    orga_service.remove_orga_flag(brand.id, user.id, admin_user.id)

    assert not is_orga_for_brand(user.id, brand.id)


def is_orga_for_brand(user_id, brand_id) -> bool:
    return orga_service.find_orga_flag(brand_id, user_id) is not None
