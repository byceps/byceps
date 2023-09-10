"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.services.orga import orga_service


def test_orga_status_changes(brand, admin_user, user):
    assert not has_orga_status(user.id, brand.id)

    orga_service.grant_orga_status(user, brand, admin_user)

    assert has_orga_status(user.id, brand.id)

    orga_service.revoke_orga_status(user, brand, admin_user)

    assert not has_orga_status(user.id, brand.id)


def has_orga_status(user_id, brand_id) -> bool:
    return orga_service.has_orga_status(user_id, brand_id)
