"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.user_badge import (
    command_service as badge_command_service,
    service as badge_service,
)
from byceps.services.user_badge.transfer.models import QuantifiedBadgeAwarding

from tests.api.helpers import assemble_authorization_header


def test_award_badge(admin_app_with_db, normal_user, admin_user):
    badge = badge_command_service.create_badge(
        'supporter', 'Supporter', 'supporter.svg'
    )

    before = badge_service.get_awardings_of_badge(badge.id)
    assert before == set()

    url = f'/api/user_badges/awardings'
    headers = [assemble_authorization_header('just-say-PLEASE')]
    form_data = {
        'badge_id': str(badge.id),
        'user_id': str(normal_user.id),
        'initiator_id': str(admin_user.id),
    }

    with admin_app_with_db.test_client() as client:
        response = client.post(url, headers=headers, data=form_data)
    assert response.status_code == 204

    actual = badge_service.get_awardings_of_badge(badge.id)
    assert actual == {QuantifiedBadgeAwarding(badge.id, normal_user.id, 1)}
