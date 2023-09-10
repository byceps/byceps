"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.orga import orga_domain_service


def test_grant_orga_status(user, brand, initiator):
    log_entry = orga_domain_service.grant_orga_status(user, brand.id, initiator)

    assert log_entry.id is not None
    assert log_entry.occurred_at is not None
    assert log_entry.event_type == 'orgaflag-added'
    assert log_entry.user_id == user.id
    assert log_entry.data == {
        'brand_id': str(brand.id),
        'initiator_id': str(initiator.id),
    }


def test_revoke_orga_status(user, brand, initiator):
    log_entry = orga_domain_service.revoke_orga_status(
        user, brand.id, initiator
    )

    assert log_entry.id is not None
    assert log_entry.occurred_at is not None
    assert log_entry.event_type == 'orgaflag-removed'
    assert log_entry.user_id == user.id
    assert log_entry.data == {
        'brand_id': str(brand.id),
        'initiator_id': str(initiator.id),
    }


@pytest.fixture(scope='module')
def initiator(make_user):
    return make_user()
